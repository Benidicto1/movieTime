from django.core.exceptions import PermissionDenied

from purchases.models import Purchase
from subscriptions.services import SubscriptionService


class MovieAccessService:

    @staticmethod
    def has_permanent_ownership(
        *,
        user,
        movie,
    ):
        if not user.is_authenticated:
            return False

        return (
            Purchase.objects
            .filter(
                user=user,
                movie=movie,
                status=Purchase.Status.PAID,
            )
            .exists()
        )

    @staticmethod
    def has_subscription_access(
        *,
        user,
    ):
        if not user.is_authenticated:
            return False

        return (
            SubscriptionService
            .has_active_subscription(
                user=user
            )
        )

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

        if MovieAccessService.has_subscription_access(
            user=user
        ):
            return True

        return MovieAccessService.has_permanent_ownership(
            user=user,
            movie=movie,
        )

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

        if not MovieAccessService.can_stream(
            user=user,
            movie=movie,
        ):
            raise PermissionDenied(
                "You do not have permission "
                "to stream this movie."
            )

        return True