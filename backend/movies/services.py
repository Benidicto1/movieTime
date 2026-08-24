from django.core.exceptions import PermissionDenied

from subscriptions.services import (
    SubscriptionService,
)
from downloads.models import PermanentDownload
from subscriptions.services import SubscriptionService



class StreamingService:

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

        has_subscription = (
            SubscriptionService.has_active_subscription(
                user=user
            )
        )

        if has_subscription:
            return True

        from downloads.models import PermanentDownload

        return PermanentDownload.objects.filter(
            user=user,
            movie=movie,
            is_available=True,
        ).exists()

    @staticmethod
    def authorize_stream(
        *,
        user,
        movie,
    ):
        if not user.is_authenticated:
            raise PermissionDenied(
                "Authentication is required."
            )

        if not movie.is_active:
            raise PermissionDenied(
                "This movie is not available."
            )

        if not SubscriptionService.has_active_subscription(
            user=user
        ):
            raise PermissionDenied(
                "An active subscription is required."
            )

        return True




class MovieAccessService:

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
    def can_stream(
        *,
        user,
        movie,
    ):
        if not user.is_authenticated:
            return False

        if not movie.is_active:
            return False

        if SubscriptionService.has_active_subscription(
            user=user,
        ):
            return True

        return MovieAccessService.has_permanent_ownership(
            user=user,
            movie=movie,
        )