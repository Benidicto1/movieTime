# backend/movies/services.py

"""
MovieTime movie access and media authorization services.

Chapter 74
-----------

This module is responsible for deciding whether an authenticated user
is allowed to access a movie.

Supported access models:

1. Permanent purchase
   - Purchase.status == PAID

2. Active subscription
   - A valid active subscription exists

Important security rules:

- The Android application must never decide whether a user owns a movie.
- The Android application must never receive private storage credentials.
- A successful payment must be confirmed by the backend.
- Movie streaming authorization must happen on the backend.
- Storage URL generation must happen only after authorization succeeds.
- A public/permanent movie URL must never be returned for protected media.

The expected streaming flow is:

    Android
       |
       | JWT
       v
    MovieStreamAPIView
       |
       v
    MovieAccessService.authorize_stream()
       |
       +---- paid purchase? ------+
       |                          |
       +---- active subscription? |
                                  |
                              authorized
                                  |
                                  v
                       MediaDeliveryService
                                  |
                                  v
                         private storage
                                  |
                                  v
                         short-lived URL
                                  |
                                  v
                              Android
"""


from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet

from purchases.models import Purchase
from subscriptions.services import SubscriptionService


class MovieAccessError(Exception):
    """Base exception for MovieTime movie-access errors."""


class MovieNotAvailableError(MovieAccessError):
    """Raised when a movie is not available for viewing."""


class MovieAuthenticationError(MovieAccessError):
    """Raised when authentication is required."""


class MovieAuthorizationError(MovieAccessError):
    """Raised when a user does not have permission to access a movie."""


@dataclass(frozen=True)
class MovieAccessResult:
    """
    Result of a movie-access authorization check.

    access_granted:
        True when the user may access the movie.

    access_type:
        One of:
            - "purchase"
            - "subscription"
            - "none"
    """

    access_granted: bool
    access_type: str


class MovieAccessService:
    """
    Centralized authorization service for MovieTime movies.

    This class deliberately contains authorization logic only.

    It does NOT generate storage URLs.

    Storage URL generation belongs to MediaDeliveryService.
    """

    PURCHASE_ACCESS = "purchase"
    SUBSCRIPTION_ACCESS = "subscription"
    NO_ACCESS = "none"

    @staticmethod
    def _is_authenticated(user: Any) -> bool:
        """
        Safely determine whether a user is authenticated.
        """

        return bool(
            user is not None
            and getattr(user, "is_authenticated", False)
        )

    @staticmethod
    def _movie_is_active(movie: Any) -> bool:
        """
        Determine whether the movie is currently available.

        MovieTime uses Movie.is_active as the publication/availability
        control.
        """

        return bool(
            movie is not None
            and getattr(movie, "is_active", False)
        )

    @staticmethod
    def get_paid_purchase(
        *,
        user: Any,
        movie: Any,
    ) -> Purchase | None:
        """
        Return a paid purchase for the specified user/movie.

        A purchase is considered permanent ownership only when its
        status is PAID.

        Pending, failed, cancelled and refunded purchases do not
        grant access.
        """

        if not MovieAccessService._is_authenticated(user):
            return None

        if movie is None:
            return None

        return (
            Purchase.objects
            .filter(
                user=user,
                movie=movie,
                status=Purchase.Status.PAID,
            )
            .order_by("-paid_at", "-created_at")
            .first()
        )

    @staticmethod
    def has_permanent_ownership(
        *,
        user: Any,
        movie: Any,
    ) -> bool:
        """
        Return True when the user permanently owns the movie.

        Permanent ownership is based on a successful Purchase.

        A download record is NOT used as proof of ownership.
        """

        return (
            MovieAccessService.get_paid_purchase(
                user=user,
                movie=movie,
            )
            is not None
        )

    @staticmethod
    def get_active_subscription(
        *,
        user: Any,
    ):
        """
        Return the user's active subscription, if one exists.

        SubscriptionService remains the authoritative service for
        subscription state.
        """

        if not MovieAccessService._is_authenticated(user):
            return None

        return SubscriptionService.get_active_subscription(user)

    @staticmethod
    def has_subscription_access(
        *,
        user: Any,
    ) -> bool:
        """
        Return True when the user has an active subscription.
        """

        if not MovieAccessService._is_authenticated(user):
            return False

        return (
            MovieAccessService.get_active_subscription(
                user=user,
            )
            is not None
        )

    @staticmethod
    def get_access_result(
        *,
        user: Any,
        movie: Any,
    ) -> MovieAccessResult:
        """
        Determine exactly why a user can access a movie.

        Access priority:

        1. Permanent purchase
        2. Active subscription
        3. No access

        A permanent purchase is checked first because it represents
        permanent ownership independently of subscription state.
        """

        if not MovieAccessService._is_authenticated(user):
            return MovieAccessResult(
                access_granted=False,
                access_type=MovieAccessService.NO_ACCESS,
            )

        if not MovieAccessService._movie_is_active(movie):
            return MovieAccessResult(
                access_granted=False,
                access_type=MovieAccessService.NO_ACCESS,
            )

        if MovieAccessService.has_permanent_ownership(
            user=user,
            movie=movie,
        ):
            return MovieAccessResult(
                access_granted=True,
                access_type=MovieAccessService.PURCHASE_ACCESS,
            )

        if MovieAccessService.has_subscription_access(
            user=user,
        ):
            return MovieAccessResult(
                access_granted=True,
                access_type=MovieAccessService.SUBSCRIPTION_ACCESS,
            )

        return MovieAccessResult(
            access_granted=False,
            access_type=MovieAccessService.NO_ACCESS,
        )

    @staticmethod
    def can_stream(
        *,
        user: Any,
        movie: Any,
    ) -> bool:
        """
        Return True when the user is authorized to stream the movie.

        Streaming is permitted when:

        - the movie is active, AND
        - the user owns the movie permanently OR
        - the user has an active subscription.
        """

        result = MovieAccessService.get_access_result(
            user=user,
            movie=movie,
        )

        return result.access_granted

    @staticmethod
    def authorize_stream(
        *,
        user: Any,
        movie: Any,
    ) -> MovieAccessResult:
        """
        Authorize movie streaming.

        Raises PermissionDenied when access is not permitted.

        Returns:
            MovieAccessResult
        """

        if not MovieAccessService._is_authenticated(user):
            raise PermissionDenied(
                "Authentication is required to stream this movie."
            )

        if movie is None:
            raise PermissionDenied(
                "Movie not found."
            )

        if not MovieAccessService._movie_is_active(movie):
            raise PermissionDenied(
                "This movie is not available."
            )

        access_result = MovieAccessService.get_access_result(
            user=user,
            movie=movie,
        )

        if not access_result.access_granted:
            raise PermissionDenied(
                "You do not have permission to stream this movie."
            )

        return access_result

    @staticmethod
    def require_stream_access(
        *,
        user: Any,
        movie: Any,
    ) -> MovieAccessResult:
        """
        Alias for authorize_stream().

        This method provides a descriptive name for callers that want
        to explicitly state that authorization is mandatory.
        """

        return MovieAccessService.authorize_stream(
            user=user,
            movie=movie,
        )

    @staticmethod
    def can_download(
        *,
        user: Any,
        movie: Any,
    ) -> bool:
        """
        Determine whether the user is allowed to initiate a download.

        Current MovieTime policy:

        - Permanent movie purchases may download.
        - Active subscriptions may download.
        - No access means no download.

        IMPORTANT:

        This method only authorizes the operation.

        It does not create a PermanentDownload record and does not
        generate a download URL.
        """

        return MovieAccessService.can_stream(
            user=user,
            movie=movie,
        )

    @staticmethod
    def authorize_download(
        *,
        user: Any,
        movie: Any,
    ) -> MovieAccessResult:
        """
        Authorize a movie download.

        Download authorization follows the same ownership/subscription
        rules as streaming.

        The actual download lifecycle belongs to the downloads app.
        """

        if not MovieAccessService._is_authenticated(user):
            raise PermissionDenied(
                "Authentication is required to download this movie."
            )

        if movie is None:
            raise PermissionDenied(
                "Movie not found."
            )

        if not MovieAccessService._movie_is_active(movie):
            raise PermissionDenied(
                "This movie is not available."
            )

        access_result = MovieAccessService.get_access_result(
            user=user,
            movie=movie,
        )

        if not access_result.access_granted:
            raise PermissionDenied(
                "You do not have permission to download this movie."
            )

        return access_result

    @staticmethod
    def get_user_purchases(
        *,
        user: Any,
    ) -> QuerySet:
        """
        Return all paid purchases belonging to the authenticated user.

        This is useful for library endpoints and ownership checks.

        The caller remains responsible for pagination/serialization.
        """

        if not MovieAccessService._is_authenticated(user):
            return Purchase.objects.none()

        return (
            Purchase.objects
            .filter(
                user=user,
                status=Purchase.Status.PAID,
            )
            .select_related("movie")
            .order_by("-paid_at", "-created_at")
        )

    @staticmethod
    def get_owned_movie_ids(
        *,
        user: Any,
    ) -> QuerySet:
        """
        Return IDs of movies permanently owned by the user.

        This returns a queryset of movie IDs rather than movie objects.
        """

        if not MovieAccessService._is_authenticated(user):
            return Purchase.objects.none().values_list(
                "movie_id",
                flat=True,
            )

        return (
            Purchase.objects
            .filter(
                user=user,
                status=Purchase.Status.PAID,
            )
            .values_list(
                "movie_id",
                flat=True,
            )
            .distinct()
        )

    @staticmethod
    def access_type(
        *,
        user: Any,
        movie: Any,
    ) -> str:
        """
        Return the user's access type.

        Possible values:

            "purchase"
            "subscription"
            "none"
        """

        return MovieAccessService.get_access_result(
            user=user,
            movie=movie,
        ).access_type

    @staticmethod
    def is_subscription_access(
        *,
        user: Any,
        movie: Any,
    ) -> bool:
        """
        Return True when access is specifically provided by an
        active subscription.
        """

        result = MovieAccessService.get_access_result(
            user=user,
            movie=movie,
        )

        return (
            result.access_granted
            and result.access_type
            == MovieAccessService.SUBSCRIPTION_ACCESS
        )

    @staticmethod
    def is_purchase_access(
        *,
        user: Any,
        movie: Any,
    ) -> bool:
        """
        Return True when access is specifically provided by permanent
        ownership.
        """

        result = MovieAccessService.get_access_result(
            user=user,
            movie=movie,
        )

        return (
            result.access_granted
            and result.access_type
            == MovieAccessService.PURCHASE_ACCESS
        )


# ---------------------------------------------------------------------
# Backwards-compatible helper functions
# ---------------------------------------------------------------------


def user_can_stream(
    *,
    user: Any,
    movie: Any,
) -> bool:
    """
    Convenience wrapper around MovieAccessService.can_stream().
    """

    return MovieAccessService.can_stream(
        user=user,
        movie=movie,
    )


def authorize_movie_stream(
    *,
    user: Any,
    movie: Any,
) -> MovieAccessResult:
    """
    Convenience wrapper around MovieAccessService.authorize_stream().
    """

    return MovieAccessService.authorize_stream(
        user=user,
        movie=movie,
    )


def user_owns_movie(
    *,
    user: Any,
    movie: Any,
) -> bool:
    """
    Convenience wrapper for permanent movie ownership.
    """

    return MovieAccessService.has_permanent_ownership(
        user=user,
        movie=movie,
    )


def user_has_subscription(
    *,
    user: Any,
) -> bool:
    """
    Convenience wrapper for active subscription access.
    """

    return MovieAccessService.has_subscription_access(
        user=user,
    )