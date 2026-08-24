from django.db import transaction
from django.utils import timezone

from subscriptions.services import SubscriptionService

from .models import PermanentDownload


class DownloadAuthorizationService:

    @staticmethod
    def can_download(
        *,
        user,
        movie,
    ):

        if not user.is_authenticated:
            return False

        if not movie.is_active:
            return False

        return (
            SubscriptionService
            .has_active_subscription(user)
        )

    @staticmethod
    @transaction.atomic
    def create_download(
        *,
        user,
        movie,
    ):

        if not (
            DownloadAuthorizationService
            .can_download(
                user=user,
                movie=movie,
            )
        ):

            raise PermissionError(
                "An active subscription "
                "is required to download "
                "this movie."
            )

        download, created = (
            PermanentDownload.objects
            .get_or_create(
                user=user,
                movie=movie,
                defaults={
                    "status": (
                        PermanentDownload
                        .Status
                        .PENDING
                    ),
                },
            )
        )

        return download, created

    @staticmethod
    def mark_downloading(
        download,
    ):

        download.status = (
            PermanentDownload
            .Status
            .DOWNLOADING
        )

        download.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return download

    @staticmethod
    def mark_completed(
        download,
    ):

        download.status = (
            PermanentDownload
            .Status
            .COMPLETED
        )

        download.downloaded_at = (
            timezone.now()
        )

        download.save(
            update_fields=[
                "status",
                "downloaded_at",
                "updated_at",
            ]
        )

        return download

    @staticmethod
    def mark_failed(
        download,
    ):

        download.status = (
            PermanentDownload
            .Status
            .FAILED
        )

        download.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return download

    @staticmethod
    def owns_movie(
        *,
        user,
        movie,
    ):

        return (
            PermanentDownload.objects
            .filter(
                user=user,
                movie=movie,
                status=(
                    PermanentDownload
                    .Status
                    .COMPLETED
                ),
            )
            .exists()
        )


class MediaAuthorizationService:

    @staticmethod
    def can_stream(
        *,
        user,
        movie,
    ):

        if not user.is_authenticated:
            return False

        if not movie.is_active:
            return False

        return (
            SubscriptionService
            .has_active_subscription(user)
        )

    @staticmethod
    def owns_permanent_download(
        *,
        user,
        movie,
    ):

        if not user.is_authenticated:
            return False

        return (
            PermanentDownload.objects
            .filter(
                user=user,
                movie=movie,
                status=(
                    PermanentDownload
                    .Status
                    .COMPLETED
                ),
            )
            .exists()
        )

    @staticmethod
    def can_access_offline(
        *,
        user,
        movie,
    ):

        return (
            MediaAuthorizationService
            .owns_permanent_download(
                user=user,
                movie=movie,
            )
        )