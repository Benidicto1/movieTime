# backend/movies/security.py

"""
MovieTime media security utilities.

Chapter 74
-----------

This module contains security checks that protect MovieTime's private
movie media namespace.

Responsibilities:

- Validate movie storage keys.
- Reject path traversal.
- Reject malformed storage keys.
- Reject public HTTP/HTTPS media URLs.
- Prevent protected movie media from accidentally using public URLs.

This module does NOT:

- authenticate users;
- determine movie ownership;
- determine subscription access;
- generate signed URLs;
- communicate with S3/R2/GCS/Azure;
- decide whether a user can watch a movie.

Authorization belongs to:

    movies.services.MovieAccessService

Signed URL generation belongs to:

    movies.storage_services.MediaDeliveryService
"""


from __future__ import annotations

from urllib.parse import unquote, urlparse

from django.core.exceptions import SuspiciousOperation


class MediaSecurityError(Exception):
    """
    Base exception for MovieTime media-security errors.
    """


class InvalidMediaKeyError(MediaSecurityError):
    """
    Raised when a movie storage key is invalid or unsafe.
    """


class PublicMediaURLRejectedError(MediaSecurityError):
    """
    Raised when protected media is supplied as a public URL.
    """


class MediaPathTraversalError(InvalidMediaKeyError):
    """
    Raised when a storage key contains path traversal.
    """


class MediaURLValidationError(InvalidMediaKeyError):
    """
    Raised when a media URL is malformed or unsafe.
    """


def validate_storage_key(storage_key: str) -> str:
    """
    Validate and normalize a private movie storage key.

    A valid storage key:

        - is not empty;
        - is not a URL;
        - does not contain backslashes;
        - does not contain '.' path components;
        - does not contain '..' path components;
        - does not contain encoded traversal;
        - does not contain null bytes;
        - does not begin with an unsafe absolute path.

    Example of an acceptable key:

        private/movies/25/movie-1080p.mp4

    Examples of rejected values:

        ../../movie.mp4
        ../private/movie.mp4
        /etc/movie.mp4
        http://example.com/movie.mp4
        https://cdn.example.com/movie.mp4
        private/../movie.mp4
        private/%2e%2e/movie.mp4
    """

    if storage_key is None:
        raise InvalidMediaKeyError(
            "Movie storage key is required."
        )

    if not isinstance(storage_key, str):
        raise InvalidMediaKeyError(
            "Movie storage key must be a string."
        )

    normalized = storage_key.strip()

    if not normalized:
        raise InvalidMediaKeyError(
            "Movie storage key cannot be empty."
        )

    # Null bytes must never be accepted.
    if "\x00" in normalized:
        raise InvalidMediaKeyError(
            "Movie storage key contains an invalid null byte."
        )

    # Backslashes can create platform-specific path traversal issues.
    if "\\" in normalized:
        raise InvalidMediaKeyError(
            "Movie storage key cannot contain backslashes."
        )

    # A storage key must never be an HTTP/HTTPS URL.
    if is_public_media_url(normalized):
        raise PublicMediaURLRejectedError(
            "Protected movie media must use a private storage key, "
            "not a public URL."
        )

    # Reject other URI schemes as well.
    parsed = urlparse(normalized)

    if parsed.scheme:
        raise InvalidMediaKeyError(
            "Movie storage key cannot contain a URI scheme."
        )

    if parsed.netloc:
        raise InvalidMediaKeyError(
            "Movie storage key cannot contain a network location."
        )

    # Decode once before checking for encoded traversal.
    decoded = unquote(normalized)

    if "\x00" in decoded:
        raise InvalidMediaKeyError(
            "Movie storage key contains an invalid encoded null byte."
        )

    # Reject encoded traversal.
    lowered = normalized.lower()

    dangerous_encoded_sequences = (
        "%2e",
        "%2f",
        "%5c",
    )

    if any(sequence in lowered for sequence in dangerous_encoded_sequences):
        raise MediaPathTraversalError(
            "Encoded path traversal is not permitted."
        )

    # Reject absolute paths.
    if normalized.startswith("/"):
        normalized = normalized.lstrip("/")

    if not normalized:
        raise InvalidMediaKeyError(
            "Movie storage key cannot be empty."
        )

    parts = normalized.split("/")

    for part in parts:
        if part == "":
            raise InvalidMediaKeyError(
                "Movie storage key contains an empty path component."
            )

        if part == ".":
            raise MediaPathTraversalError(
                "Movie storage key cannot contain '.' path components."
            )

        if part == "..":
            raise MediaPathTraversalError(
                "Movie storage key cannot contain '..' path components."
            )

    # Check the decoded value as an additional defense.
    decoded_parts = decoded.lstrip("/").split("/")

    for part in decoded_parts:
        if part in {".", ".."}:
            raise MediaPathTraversalError(
                "Movie storage key contains encoded path traversal."
            )

    return normalized


def is_public_media_url(value: str | None) -> bool:
    """
    Return True when a value is an HTTP or HTTPS URL.

    Protected MovieTime movie media should not be stored or returned
    as permanent public URLs.
    """

    if not value:
        return False

    if not isinstance(value, str):
        return False

    normalized = value.strip()

    if not normalized:
        return False

    try:
        parsed = urlparse(normalized)
    except ValueError:
        return False

    return parsed.scheme.lower() in {
        "http",
        "https",
    }


def reject_public_media_url(url: str | None) -> None:
    """
    Reject a public HTTP/HTTPS media URL.

    This is useful when validating movie media before it reaches the
    storage-delivery layer.
    """

    if not url:
        return

    if is_public_media_url(url):
        raise PublicMediaURLRejectedError(
            "Protected movie media cannot use a public URL. "
            "Use a private storage key instead."
        )


def validate_private_media_key(
    storage_key: str,
    *,
    required_prefix: str | None = None,
) -> str:
    """
    Validate that a movie storage key belongs to the private media
    namespace.

    Example:

        validate_private_media_key(
            "private/movies/25/movie.mp4",
            required_prefix="private/movies/",
        )

    This provides an additional namespace boundary so that a movie
    cannot request an arbitrary object from the storage bucket.
    """

    normalized_key = validate_storage_key(storage_key)

    if required_prefix is None:
        return normalized_key

    if not isinstance(required_prefix, str):
        raise InvalidMediaKeyError(
            "Private media prefix must be a string."
        )

    normalized_prefix = required_prefix.strip()

    if normalized_prefix and not normalized_prefix.endswith("/"):
        normalized_prefix += "/"

    if normalized_prefix and not normalized_key.startswith(
        normalized_prefix
    ):
        raise InvalidMediaKeyError(
            "Movie storage key does not belong to the private "
            "movie-media namespace."
        )

    return normalized_key


def validate_media_filename(filename: str) -> str:
    """
    Validate the final filename component of a movie media object.

    This is primarily useful when generating or importing storage keys.
    """

    if filename is None:
        raise InvalidMediaKeyError(
            "Media filename is required."
        )

    if not isinstance(filename, str):
        raise InvalidMediaKeyError(
            "Media filename must be a string."
        )

    normalized = filename.strip()

    if not normalized:
        raise InvalidMediaKeyError(
            "Media filename cannot be empty."
        )

    if normalized in {".", ".."}:
        raise MediaPathTraversalError(
            "Invalid media filename."
        )

    if "/" in normalized or "\\" in normalized:
        raise InvalidMediaKeyError(
            "Media filename cannot contain path separators."
        )

    if "\x00" in normalized:
        raise InvalidMediaKeyError(
            "Media filename contains an invalid null byte."
        )

    if "%" in normalized:
        decoded = unquote(normalized)

        if decoded != normalized:
            raise InvalidMediaKeyError(
                "Encoded media filenames are not permitted."
            )

    return normalized


def build_private_storage_key(
    *,
    private_prefix: str,
    movie_id: int,
    filename: str,
) -> str:
    """
    Safely construct a MovieTime private storage key.

    Example result:

        private/movies/25/movie.mp4
    """

    if movie_id is None:
        raise InvalidMediaKeyError(
            "Movie ID is required."
        )

    try:
        normalized_movie_id = int(movie_id)
    except (TypeError, ValueError) as exc:
        raise InvalidMediaKeyError(
            "Movie ID must be an integer."
        ) from exc

    if normalized_movie_id <= 0:
        raise InvalidMediaKeyError(
            "Movie ID must be greater than zero."
        )

    if not private_prefix:
        raise InvalidMediaKeyError(
            "Private media prefix is required."
        )

    normalized_prefix = private_prefix.strip().strip("/")

    if not normalized_prefix:
        raise InvalidMediaKeyError(
            "Private media prefix cannot be empty."
        )

    normalized_filename = validate_media_filename(filename)

    storage_key = (
        f"{normalized_prefix}/"
        f"{normalized_movie_id}/"
        f"{normalized_filename}"
    )

    return validate_storage_key(storage_key)


def secure_media_value(value: str | None) -> str | None:
    """
    Validate a media value before it is used by protected-media code.

    This function accepts only private storage keys.

    Public URLs are explicitly rejected.
    """

    if value is None:
        return None

    normalized = value.strip()

    if not normalized:
        return None

    reject_public_media_url(normalized)

    return validate_storage_key(normalized)


def raise_django_suspicious_operation(
    message: str,
) -> None:
    """
    Raise Django's SuspiciousOperation exception.

    This can be used at request boundaries when malformed media
    identifiers should be treated as suspicious input.
    """

    raise SuspiciousOperation(message)