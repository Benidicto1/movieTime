from datetime import timedelta

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
        plan = (
            SubscriptionPlan.objects
            .filter(
                id=plan_id,
                is_active=True,
            )
            .first()
        )

        if plan is None:
            raise ValueError(
                "Subscription plan not found."
            )

        order = (
            SubscriptionOrder.objects.create(
                user=user,
                plan=plan,
                amount=plan.price,
                currency="UGX",
                status=(
                    SubscriptionOrder
                    .Status
                    .PENDING
                ),
            )
        )

        return order

    @staticmethod
    def get_active_subscription(
        user,
    ):
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
    def has_active_subscription(
        user,
    ):
        return (
            SubscriptionService
            .get_active_subscription(user)
            is not None
        )

    @staticmethod
    def can_stream(
        user,
    ):
        return (
            SubscriptionService
            .has_active_subscription(user)
        )

    @staticmethod
    @transaction.atomic
    def activate_subscription(
        *,
        order,
    ):
        order = (
            SubscriptionOrder.objects
            .select_for_update()
            .select_related("plan")
            .get(
                pk=order.pk
            )
        )

        if order.subscription_id:
            return order.subscription

        if (
            order.status
            != SubscriptionOrder.Status.PAID
        ):
            raise ValueError(
                "Subscription order has "
                "not been paid."
            )

        now = timezone.now()

        existing_subscription = (
            Subscription.objects
            .select_for_update()
            .filter(
                user=order.user,
                status=Subscription.Status.ACTIVE,
                expires_at__gt=now,
            )
            .order_by("-expires_at")
            .first()
        )

        if existing_subscription:
            start_date = (
                existing_subscription
                .expires_at
            )
        else:
            start_date = now

        expires_at = (
            start_date
            + timedelta(
                days=order.plan.duration_days
            )
        )

        subscription = (
            Subscription.objects.create(
                user=order.user,
                plan=order.plan,
                status=(
                    Subscription
                    .Status
                    .ACTIVE
                ),
                started_at=start_date,
                expires_at=expires_at,
            )
        )

        order.subscription = subscription

        order.save(
            update_fields=[
                "subscription",
                "updated_at",
            ]
        )

        return subscription

    @staticmethod
    def expire_subscriptions():

        now = timezone.now()

        return (
            Subscription.objects
            .filter(
                status=(
                    Subscription
                    .Status
                    .ACTIVE
                ),
                expires_at__lte=now,
            )
            .update(
                status=(
                    Subscription
                    .Status
                    .EXPIRED
                ),
            )
        )