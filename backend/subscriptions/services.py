from django.db import transaction
from django.utils import timezone

from .models import (
    Subscription,
    SubscriptionOrder,
    SubscriptionPlan,
)


class SubscriptionService:

    @staticmethod
    @transaction.atomic
    def create_order(
        *,
        user,
        plan_id,
    ):

        plan = SubscriptionPlan.objects.filter(
            id=plan_id,
            is_active=True,
        ).first()

        if plan is None:
            raise ValueError(
                "Subscription plan not found."
            )

        order = SubscriptionOrder.objects.create(
            user=user,
            plan=plan,
            amount=plan.price,
            currency="UGX",
            status=(
                SubscriptionOrder.Status.PENDING
            ),
        )

        return order

    @staticmethod
    def get_active_subscription(user):

        now = timezone.now()

        return (
            Subscription.objects
            .filter(
                user=user,
                status=Subscription.Status.ACTIVE,
                started_at__lte=now,
                expires_at__gt=now,
            )
            .select_related("plan")
            .order_by("-expires_at")
            .first()
        )

    @staticmethod
    def has_active_subscription(user):

        return (
            SubscriptionService
            .get_active_subscription(user)
            is not None
        )

    @staticmethod
    def can_stream(user):

        return SubscriptionService.has_active_subscription(
            user
        )

    @staticmethod
    def expire_subscriptions():

        now = timezone.now()

        return (
            Subscription.objects
            .filter(
                status=Subscription.Status.ACTIVE,
                expires_at__lte=now,
            )
            .update(
                status=Subscription.Status.EXPIRED,
            )
        )