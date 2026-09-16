# backend/movies/storage_services.py

"""
MovieTime private media storage services.

Chapter 74
------------

Responsibilities:

- Validate private movie storage keys.
- Prevent path traversal.
- Prevent accidental use of public movie URLs.
- Generate short-lived signed media URLs through a storage adapter.
- Keep storage-provider-specific implementation separate from
  movie authorization logic.

Important:

This module does NOT decide whether a user is allowed to watch a movie.

Authorization happens before this service is called.

The expected flow is:

    User
      |
      v
    MovieStreamAPIView
      |
      v
    MediaAuthorizationService
      |
      | authorized
      v
    MediaDeliveryService
      |
      v
    PrivateStorageAdapter
      |
      v
    Short-lived signed URL
      |
      v
    Android / ExoPlayer
"""


from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from django.conf import settings


# ============================================================================
# EXCEPTIONS
# ============================================================================


class StorageError(Exception):
    """
    Base exception for MovieTime storage errors.
    """


class StorageConfigurationError(StorageError):
    """
    Raised when private storage is incorrectly configured.
    """


class StorageKeyError(StorageError):
    """
    Raised when a movie storage key is invalid.
    """


class StorageURLGenerationError(StorageError):
    """
    Raised when a signed URL cannot be generated.
    """


class PublicMediaURLRejectedError(StorageError):
    """
    Raised when a public/permanent media URL is supplied where a
    private storage key is required.
    """


# ============================================================================
# SIGNED URL RESULT
# ============================================================================


@dataclass(frozen=True)
class SignedMediaURL:
    """
    Represents a temporary URL used to access protected movie media.
    """

    url: str
    expires_in: int


# ============================================================================
# STORAGE KEY VALIDATION
# ============================================================================


class StorageKeyValidator:
    """
    Validates movie storage keys before they are sent to a storage provider.
    """

    @staticmethod
    def validate(storage_key: str) -> str:
        """
        Validate and normalize a private storage key.

        Example of a valid key:

            private/movies/15/movie-1080p.mp4

        Invalid examples:

            ../movie.mp4
            ../../movie.mp4
            /absolute/path/movie.mp4
            https://example.com/movie.mp4
            http://example.com/movie.mp4
            private/../movie.mp4
        """

        if storage_key is None:
            raise StorageKeyError(
                "Movie storage key is required."
            )

        normalized = str(storage_key).strip()

        if not normalized:
            raise StorageKeyError(
                "Movie storage key cannot be empty."
            )

        # Backslashes are rejected to prevent Windows-style traversal
        # and inconsistent path interpretation.
        if "\\" in normalized:
            raise StorageKeyError(
                "Movie storage key cannot contain backslashes."
            )

        # A storage key must never be a URL.
        parsed = urlparse(normalized)

        if parsed.scheme or parsed.netloc:
            raise PublicMediaURLRejectedError(
                "Movie media must use a private storage key, "
                "not a public URL."
            )

        # Remove a leading slash because storage keys are relative.
        normalized = normalized.lstrip("/")

        if not normalized:
            raise StorageKeyError(
                "Movie storage key cannot be empty."
            )

        parts = normalized.split("/")

        # Reject path traversal.
        for part in parts:

            if part in {"", "."}:
                raise StorageKeyError(
                    "Movie storage key contains an invalid path component."
                )

            if part == "..":
                raise StorageKeyError(
                    "Movie storage key cannot contain '..'."
                )

        # Defense against encoded traversal being accidentally passed
        # to another storage layer.
        lowered = normalized.lower()

        if "%2e" in lowered:
            raise StorageKeyError(
                "Encoded path traversal is not permitted."
            )

        return normalized


# ============================================================================
# EXPIRATION CONFIGURATION
# ============================================================================


class StorageConfiguration:
    """
    Centralized configuration for protected movie media.
    """

    @staticmethod
    def get_bucket() -> str:
        """
        Return the configured private storage bucket/container.
        """

        bucket = getattr(
            settings,
            "MOVIETIME_STORAGE_BUCKET",
            None,
        )

        if not bucket:
            raise StorageConfigurationError(
                "MOVIETIME_STORAGE_BUCKET is not configured."
            )

        return str(bucket).strip()

    @staticmethod
    def get_private_prefix() -> str:
        """
        Return the private movie storage prefix.
        """

        prefix = getattr(
            settings,
            "MOVIETIME_STORAGE_PRIVATE_PREFIX",
            "private/movies/",
        )

        prefix = str(prefix).strip()

        if prefix and not prefix.endswith("/"):
            prefix += "/"

        return prefix

    @staticmethod
    def get_signed_url_expiration() -> int:
        """
        Return the default lifetime of a signed URL.
        """

        expiration = getattr(
            settings,
            "MOVIETIME_SIGNED_URL_EXPIRATION",
            600,
        )

        try:
            expiration = int(expiration)
        except (TypeError, ValueError) as exc:
            raise StorageConfigurationError(
                "MOVIETIME_SIGNED_URL_EXPIRATION must be an integer."
            ) from exc

        if expiration <= 0:
            raise StorageConfigurationError(
                "MOVIETIME_SIGNED_URL_EXPIRATION must be greater than zero."
            )

        return expiration

    @staticmethod
    def private_storage_required() -> bool:
        """
        Determine whether MovieTime requires private media storage.
        """

        return bool(
            getattr(
                settings,
                "MOVIETIME_REQUIRE_PRIVATE_STORAGE",
                True,
            )
        )

    @staticmethod
    def public_media_allowed() -> bool:
        """
        Determine whether public movie URLs are allowed.

        For protected MovieTime movies this should remain False.
        """

        return bool(
            getattr(
                settings,
                "MOVIETIME_ALLOW_PUBLIC_MEDIA_URLS",
                False,
            )
        )


# ============================================================================
# STORAGE ADAPTER
# ============================================================================


class PrivateStorageAdapter:
    """
    Interface for private object storage.

    A production implementation should be provided for the selected
    storage provider, for example:

        - Amazon S3
        - Cloudflare R2
        - Google Cloud Storage
        - Azure Blob Storage

    This base implementation intentionally refuses to create a fake
    "signed URL".

    Returning a normal public URL here would defeat Chapter 74's
    security objective.
    """

    provider_name = "UNCONFIGURED"

    def generate_signed_url(
        self,
        *,
        storage_key: str,
        expires_in: int,
    ) -> SignedMediaURL:
        """
        Generate a short-lived signed URL.

        Concrete storage adapters must override this method.
        """

        raise StorageURLGenerationError(
            "Private storage signing is not configured. "
            "Configure a production storage adapter before "
            "serving protected movie media."
        )


# ============================================================================
# STORAGE SERVICE
# ============================================================================


class MediaStorageService:
    """
    Application-facing storage service.

    This class hides storage-provider details from the rest of MovieTime.
    """

    def __init__(
        self,
        adapter: Optional[PrivateStorageAdapter] = None,
    ):
        self.adapter = adapter or PrivateStorageAdapter()

    def normalize_storage_key(
        self,
        storage_key: str,
    ) -> str:
        """
        Validate a storage key and ensure it belongs to the private
        movie-media namespace.
        """

        normalized = StorageKeyValidator.validate(
            storage_key
        )

        private_prefix = (
            StorageConfiguration.get_private_prefix()
        )

        if private_prefix:

            # Prevent a movie object from referencing a completely
            # unrelated object in the storage bucket.
            if not normalized.startswith(private_prefix):

                raise StorageKeyError(
                    "Movie storage key must belong to the "
                    "private movie-media namespace."
                )

        return normalized

    def generate_signed_url(
        self,
        *,
        storage_key: str,
        expires_in: Optional[int] = None,
    ) -> SignedMediaURL:
        """
        Generate a short-lived signed URL for protected movie media.
        """

        normalized_key = self.normalize_storage_key(
            storage_key
        )

        if expires_in is None:
            expires_in = (
                StorageConfiguration
                .get_signed_url_expiration()
            )
        else:

            try:
                expires_in = int(expires_in)
            except (TypeError, ValueError) as exc:

                raise StorageURLGenerationError(
                    "expires_in must be an integer."
                ) from exc

        if expires_in <= 0:

            raise StorageURLGenerationError(
                "Signed URL expiration must be greater than zero."
            )

        # Protect against accidentally requesting extremely long-lived
        # URLs from application code.
        maximum_expiration = 3600

        if expires_in > maximum_expiration:

            raise StorageURLGenerationError(
                "Protected movie URLs cannot live longer than "
                "one hour."
            )

        return self.adapter.generate_signed_url(
            storage_key=normalized_key,
            expires_in=expires_in,
        )


# ============================================================================
# MEDIA DELIVERY SERVICE
# ============================================================================


class MediaDeliveryService:
    """
    High-level media delivery service.

    This service is intentionally concerned only with media delivery.

    It does NOT determine whether the user owns a movie.

    Authorization must happen before this service is called.
    """

    def __init__(
        self,
        storage_service: Optional[MediaStorageService] = None,
    ):
        self.storage_service = (
            storage_service
            or MediaStorageService()
        )

    def get_stream_url(
        self,
        *,
        storage_key: str,
        expires_in: Optional[int] = None,
    ) -> SignedMediaURL:
        """
        Generate a temporary stream URL.
        """

        return self.storage_service.generate_signed_url(
            storage_key=storage_key,
            expires_in=expires_in,
        )


# ============================================================================
# SECURITY HELPERS
# ============================================================================


def is_public_url(value: str) -> bool:
    """
    Determine whether a value appears to be an HTTP/HTTPS URL.
    """

    if not value:
        return False

    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False

    return parsed.scheme.lower() in {
        "http",
        "https",
    }


def reject_public_movie_url(value: str) -> None:
    """
    Reject a permanent HTTP/HTTPS movie URL.

    Protected MovieTime media must be represented by a storage key.
    """

    if is_public_url(value):

        raise PublicMediaURLRejectedError(
            "Protected movie media cannot use a public URL. "
            "Use a private storage key instead."
        )


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================


def generate_signed_url(
    *,
    storage_key: str,
    expires_in: Optional[int] = None,
    storage_service: Optional[MediaStorageService] = None,
) -> SignedMediaURL:
    """
    Convenience wrapper used by application services.
    """

    service = (
        storage_service
        or MediaStorageService()
    )

    return service.generate_signed_url(
        storage_key=storage_key,
        expires_in=expires_in,
    )