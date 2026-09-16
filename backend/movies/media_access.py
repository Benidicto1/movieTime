# backend/movies/media_access.py

"""
MovieTime protected media access.

Chapter 75
-----------

This service coordinates:

    authorization
        +
    private storage-key validation
        +
    signed media URL generation

Streaming and downloading are different application operations,
but both ultimately require protected media delivery.
"""


from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from django.core.exceptions import PermissionDenied

from .security import (
    InvalidMediaKeyError,
    PublicMediaURLRejectedError,
    validate_private_media_key,
)
from .services import (
    MovieAccessResult,
    MovieAccessService,
)
from .storage_services import (
    MediaDeliveryService,
    SignedMediaURL,
    StorageConfiguration,
    StorageError,
)


class MediaAccessError(Exception):
    """Base exception for protected media access."""


class MediaAccessDeniedError(MediaAccessError):
    """Raised when media access is not authorized."""


class MediaNotConfiguredError(MediaAccessError):
    """Raised when movie media is not configured."""


class MediaUnavailableError(MediaAccessError):
    """Raised when protected media cannot be delivered."""


@dataclass(frozen=True)
class MediaAccessResult:
    """
    Result of authorized protected-media delivery.
    """

    access_granted: bool
    access_type: str
    stream_url: str
    expires_in: int


class MediaAccessService:
    """
    Coordinates MovieTime authorization and protected media delivery.
    """

    def __init__(
        self,
        delivery_service: Optional[MediaDeliveryService] = None,
    ):
        self.delivery_service = (
            delivery_service
            or MediaDeliveryService()
        )

    # -----------------------------------------------------------------
    # Storage key
    # -----------------------------------------------------------------

    @staticmethod
    def get_movie_storage_key(
        movie: Any,
    ) -> str:
        """
        Resolve the movie's private storage key.
        """

        if movie is None:
            raise MediaNotConfiguredError(
                "Movie does not exist."
            )

        movie_media = getattr(
            movie,
            "media",
            None,
        )

        if movie_media is not None:
            storage_key = getattr(
                movie_media,
                "movie_storage_key",
                None,
            )

            if storage_key:
                return str(storage_key).strip()

        storage_key = getattr(
            movie,
            "movie_storage_key",
            None,
        )

        if storage_key:
            return str(storage_key).strip()

        raise MediaNotConfiguredError(
            "Protected movie media has not been configured."
        )

    @staticmethod
    def validate_movie_storage_key(
        storage_key: str,
    ) -> str:
        """
        Validate that the storage key belongs to the private movie
        namespace.
        """

        private_prefix = StorageConfiguration.get_private_prefix()

        return validate_private_media_key(
            storage_key,
            required_prefix=private_prefix,
        )

    # -----------------------------------------------------------------
    # Authorization
    # -----------------------------------------------------------------

    @staticmethod
    def authorize(
        *,
        user: Any,
        movie: Any,
    ) -> MovieAccessResult:
        """
        Authorize access through MovieAccessService.
        """

        try:
            return MovieAccessService.authorize_stream(
                user=user,
                movie=movie,
            )

        except PermissionDenied as exc:
            raise MediaAccessDeniedError(
                str(exc)
                or "You do not have permission to access this movie."
            ) from exc

    @staticmethod
    def authorize_download(
        *,
        user: Any,
        movie: Any,
    ) -> MovieAccessResult:
        """
        Authorize download access.

        Download authorization remains separate from streaming
        authorization even though the current MovieTime access policy
        uses the same purchase/subscription rules.
        """

        try:
            return MovieAccessService.authorize_download(
                user=user,
                movie=movie,
            )

        except PermissionDenied as exc:
            raise MediaAccessDeniedError(
                str(exc)
                or "You do not have permission to download this movie."
            ) from exc

    # -----------------------------------------------------------------
    # URL generation
    # -----------------------------------------------------------------

    def generate_stream_url(
        self,
        *,
        movie: Any,
    ) -> SignedMediaURL:
        """
        Generate a short-lived signed URL.

        Authorization must already have succeeded.
        """

        storage_key = self.get_movie_storage_key(
            movie,
        )

        validated_key = self.validate_movie_storage_key(
            storage_key,
        )

        try:
            return self.delivery_service.get_stream_url(
                storage_key=validated_key,
            )

        except (
            PublicMediaURLRejectedError,
            InvalidMediaKeyError,
        ):
            raise

        except StorageError as exc:
            raise MediaUnavailableError(
                "Protected movie media is temporarily unavailable."
            ) from exc

    # -----------------------------------------------------------------
    # Complete streaming access
    # -----------------------------------------------------------------

    def get_stream_access(
        self,
        *,
        user: Any,
        movie: Any,
    ) -> MediaAccessResult:
        """
        Authorize a user and generate a temporary stream URL.
        """

        access = self.authorize(
            user=user,
            movie=movie,
        )

        signed_media = self.generate_stream_url(
            movie=movie,
        )

        return MediaAccessResult(
            access_granted=True,
            access_type=access.access_type,
            stream_url=signed_media.url,
            expires_in=signed_media.expires_in,
        )

    # -----------------------------------------------------------------
    # Download media access
    # -----------------------------------------------------------------

    def get_download_access(
        self,
        *,
        user: Any,
        movie: Any,
    ) -> MediaAccessResult:
        """
        Authorize a user and generate a temporary media URL suitable
        for the download operation.

        The actual download record remains managed by downloads/.
        """

        access = self.authorize_download(
            user=user,
            movie=movie,
        )

        signed_media = self.generate_stream_url(
            movie=movie,
        )

        return MediaAccessResult(
            access_granted=True,
            access_type=access.access_type,
            stream_url=signed_media.url,
            expires_in=signed_media.expires_in,
        )

    # -----------------------------------------------------------------
    # Convenience checks
    # -----------------------------------------------------------------

    @staticmethod
    def can_access(
        *,
        user: Any,
        movie: Any,
    ) -> bool:
        return MovieAccessService.can_stream(
            user=user,
            movie=movie,
        )

    @staticmethod
    def can_download(
        *,
        user: Any,
        movie: Any,
    ) -> bool:
        return MovieAccessService.can_download(
            user=user,
            movie=movie,
        )


def get_protected_stream_url(
    *,
    user: Any,
    movie: Any,
) -> MediaAccessResult:
    """
    Authorize and generate a protected stream URL.
    """

    return MediaAccessService().get_stream_access(
        user=user,
        movie=movie,
    )


def get_protected_download_url(
    *,
    user: Any,
    movie: Any,
) -> MediaAccessResult:
    """
    Authorize and generate a protected download URL.
    """

    return MediaAccessService().get_download_access(
        user=user,
        movie=movie,
    )


def can_access_movie_media(
    *,
    user: Any,
    movie: Any,
) -> bool:
    """
    Check protected media access without generating a URL.
    """

    return MediaAccessService.can_access(
        user=user,
        movie=movie,
    )


def can_download_movie_media(
    *,
    user: Any,
    movie: Any,
) -> bool:
    """
    Check download authorization without generating a URL.
    """

    return MediaAccessService.can_download(
        user=user,
        movie=movie,
    )