"""
MovieTime download services.

Chapter 78 — Abuse Prevention

Download access is backend-authoritative.

A user may download a movie when:

    1. The movie is active, AND
    2. The user has a PAID permanent purchase OR
       an active subscription.

Important:

PermanentDownload is NOT proof of ownership.

Permanent ownership comes from:

    purchases.Purchase(status=PAID)

Subscription access comes from:

    subscriptions.Subscription

The downloads application is responsible for:

    - authorization;
    - creating download records;
    - tracking download state;
    - recording completion/failure;
    - exposing the user's download library.

Movie authorization is delegated to:

    movies.services.MovieAccessService
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from movies.models import Movie
from movies.services import MovieAccessResult, MovieAccessService

from .models import PermanentDownload


class DownloadError(Exception):
    """Base exception for MovieTime download errors."""


class DownloadAuthorizationError(DownloadError):
    """Raised when a user is not authorized to download a movie."""


class DownloadStateError(DownloadError):
    """Raised when an invalid download-state transition is attempted."""


class DownloadNotFoundError(DownloadError):
    """Raised when a requested download does not exist."""


class DownloadService:
    """
    Main application service for MovieTime downloads.
    """

    @staticmethod
    def _is_authenticated(user: Any) -> bool:
        return bool(
            user is not None
            and getattr(user, "is_authenticated", False)
        )

    # ================================================================
    # AUTHORIZATION
    # ================================================================

    @staticmethod
    def get_authorization(
        *,
        user: Any,
        movie: Movie,
    ) -> MovieAccessResult:
        """
        Determine whether the user may download the movie.

        Authorization is based on:

            PAID purchase
                OR
            active subscription
        """

        if not DownloadService._is_authenticated(user):
            raise DownloadAuthorizationError(
                "Authentication is required to download this movie."
            )

        if movie is None:
            raise DownloadAuthorizationError(
                "Movie not found."
            )

        try:
            return MovieAccessService.authorize_download(
                user=user,
                movie=movie,
            )

        except PermissionDenied as exc:
            raise DownloadAuthorizationError(
                str(exc)
                or "You do not have permission to download this movie."
            ) from exc

    @staticmethod
    def can_download(
        *,
        user: Any,
        movie: Movie,
    ) -> bool:
        """
        Return True when the user may download the movie.
        """

        if not DownloadService._is_authenticated(user):
            return False

        if movie is None:
            return False

        return MovieAccessService.can_download(
            user=user,
            movie=movie,
        )

    # ================================================================
    # MOVIE LOOKUP
    # ================================================================

    @staticmethod
    def get_movie(movie_id: int) -> Movie:
        """
        Retrieve an active movie.
        """

        try:
            return Movie.objects.get(
                id=movie_id,
                is_active=True,
            )
        except Movie.DoesNotExist as exc:
            raise DownloadAuthorizationError(
                "Movie not found."
            ) from exc

    # ================================================================
    # DOWNLOAD LOOKUP
    # ================================================================

    @staticmethod
    def get_download(
        *,
        user: Any,
        movie: Movie,
    ) -> PermanentDownload | None:
        """
        Return the user's download record for a movie.
        """

        if not DownloadService._is_authenticated(user):
            return None

        return (
            PermanentDownload.objects
            .filter(
                user=user,
                movie=movie,
            )
            .first()
        )

    @staticmethod
    def get_download_or_raise(
        *,
        user: Any,
        download_id: int,
    ) -> PermanentDownload:
        """
        Return a user's download record or raise an error.

        Object ownership is enforced in the database query.
        """

        download = (
            PermanentDownload.objects
            .filter(
                id=download_id,
                user=user,
            )
            .select_related("movie")
            .first()
        )

        if download is None:
            raise DownloadNotFoundError(
                "Download not found."
            )

        return download

    # ================================================================
    # CREATE DOWNLOAD
    # ================================================================

    @staticmethod
    @transaction.atomic
    def create_download(
        *,
        user: Any,
        movie: Movie,
    ) -> PermanentDownload:
        """
        Authorize and create/retrieve a download record.

        The operation is idempotent for a user/movie pair.
        """

        DownloadService.get_authorization(
            user=user,
            movie=movie,
        )

        download = (
            PermanentDownload.objects
            .select_for_update()
            .filter(
                user=user,
                movie=movie,
            )
            .first()
        )

        if download is not None:
            return download

        return PermanentDownload.objects.create(
            user=user,
            movie=movie,
            status=PermanentDownload.Status.PENDING,
        )

    # ================================================================
    # DOWNLOAD STATE
    # ================================================================

    @staticmethod
    @transaction.atomic
    def mark_downloading(
        *,
        download_id: int,
        user: Any,
    ) -> PermanentDownload:
        """
        Change a PENDING download to DOWNLOADING.
        """

        download = DownloadService.get_download_or_raise(
            user=user,
            download_id=download_id,
        )

        allowed_states = {
            PermanentDownload.Status.PENDING,
            PermanentDownload.Status.DOWNLOADING,
        }

        if download.status not in allowed_states:
            raise DownloadStateError(
                f"Cannot start download from state '{download.status}'."
            )

        if download.status != PermanentDownload.Status.DOWNLOADING:
            download.status = PermanentDownload.Status.DOWNLOADING
            download.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return download

    @staticmethod
    @transaction.atomic
    def mark_completed(
        *,
        download_id: int,
        user: Any,
    ) -> PermanentDownload:
        """
        Mark a download as completed.
        """

        download = DownloadService.get_download_or_raise(
            user=user,
            download_id=download_id,
        )

        allowed_states = {
            PermanentDownload.Status.DOWNLOADING,
            PermanentDownload.Status.COMPLETED,
        }

        if download.status not in allowed_states:
            raise DownloadStateError(
                f"Cannot complete download from state '{download.status}'."
            )

        if download.status != PermanentDownload.Status.COMPLETED:
            download.status = PermanentDownload.Status.COMPLETED
            download.downloaded_at = timezone.now()

            download.save(
                update_fields=[
                    "status",
                    "downloaded_at",
                    "updated_at",
                ]
            )

        return download

    @staticmethod
    @transaction.atomic
    def mark_failed(
        *,
        download_id: int,
        user: Any,
    ) -> PermanentDownload:
        """
        Mark a download as failed.
        """

        download = DownloadService.get_download_or_raise(
            user=user,
            download_id=download_id,
        )

        if download.status == PermanentDownload.Status.COMPLETED:
            raise DownloadStateError(
                "A completed download cannot be marked as failed."
            )

        download.status = PermanentDownload.Status.FAILED

        download.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return download

    # ================================================================
    # USER DOWNLOAD LIBRARY
    # ================================================================

    @staticmethod
    def get_user_downloads(
        *,
        user: Any,
    ):
        """
        Return only downloads belonging to the authenticated user.
        """

        if not DownloadService._is_authenticated(user):
            return PermanentDownload.objects.none()

        return (
            PermanentDownload.objects
            .filter(user=user)
            .select_related("movie")
            .order_by("-created_at")
        )

    @staticmethod
    def has_completed_download(
        *,
        user: Any,
        movie: Movie,
    ) -> bool:
        """
        Check download state.

        This is NOT an ownership check.
        """

        return (
            PermanentDownload.objects
            .filter(
                user=user,
                movie=movie,
                status=PermanentDownload.Status.COMPLETED,
            )
            .exists()
        )

    @staticmethod
    def reauthorize_download(
        *,
        user: Any,
        movie: Movie,
    ) -> MovieAccessResult:
        """
        Re-check movie authorization before a download begins.
        """

        return DownloadService.get_authorization(
            user=user,
            movie=movie,
        )


# ====================================================================
# DOWNLOAD AUTHORIZATION FACADE
# ====================================================================

class DownloadAuthorizationService:
    """
    Compatibility and API-facing authorization service.

    Views should use this class when they only need to answer:

        "Can this user download this movie?"
    """

    @staticmethod
    def can_download(
        *,
        user: Any,
        movie_id: int,
    ) -> bool:
        """
        Return whether the user may download the movie.
        """

        if not DownloadService._is_authenticated(user):
            return False

        try:
            movie = DownloadService.get_movie(movie_id)
        except DownloadAuthorizationError:
            return False

        return DownloadService.can_download(
            user=user,
            movie=movie,
        )

    @staticmethod
    def authorize(
        *,
        user: Any,
        movie_id: int,
    ) -> MovieAccessResult:
        """
        Authorize a movie download and return the access result.
        """

        movie = DownloadService.get_movie(movie_id)

        return DownloadService.get_authorization(
            user=user,
            movie=movie,
        )


# ====================================================================
# COMPATIBILITY HELPERS
# ====================================================================

def user_can_download(
    *,
    user: Any,
    movie: Movie,
) -> bool:
    return DownloadService.can_download(
        user=user,
        movie=movie,
    )


def create_authorized_download(
    *,
    user: Any,
    movie: Movie,
) -> PermanentDownload:
    return DownloadService.create_download(
        user=user,
        movie=movie,
    )


def get_user_downloads(
    *,
    user: Any,
):
    return DownloadService.get_user_downloads(
        user=user,
    )