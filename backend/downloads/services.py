from django.db import transaction

from subscriptions.services import SubscriptionService

from .models import Download, PermanentDownload


class DownloadAuthorizationService:

    @staticmethod
    def has_permanent_ownership(
        *,
        user,
        movie,
    ):
        return PermanentDownload.objects.filter(
            user=user,
            movie=movie,
            is_available=True,
        ).exists()

    @staticmethod
    def can_download(
        *,
        user,
        movie,
    ):
        return DownloadAuthorizationService.has_permanent_ownership(
            user=user,
            movie=movie,
        )

    @staticmethod
    @transaction.atomic
    def create_permanent_download(
        *,
        user,
        movie,
    ):
        if not SubscriptionService.has_active_subscription(user):
            raise PermissionError(
                "An active subscription is required "
                "to purchase a permanent download."
            )

        download, created = (
            PermanentDownload.objects.get_or_create(
                user=user,
                movie=movie,
                defaults={
                    "is_available": True,
                },
            )
        )

        if not download.is_available:
            download.is_available = True
            download.save(
                update_fields=["is_available"]
            )

        return download, created