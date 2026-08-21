from django.db import models
from django.conf import settings
from django.utils import timezone


class SubscriptionPlan(models.Model):

    class PlanType(models.TextChoices):
        DAY = "DAY", "Day"
        WEEK = "WEEK", "Week"
        MONTH = "MONTH", "Month"

    name = models.CharField(
        max_length=50,
    )

    plan_type = models.CharField(
        max_length=10,
        choices=PlanType.choices,
        unique=True,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    duration_days = models.PositiveIntegerField()

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):

        return (
            f"{self.name} - "
            f"UGX {self.price}"
        )


class Subscription(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def is_active(self):

        now = timezone.now()

        return (
            self.status == self.Status.ACTIVE
            and self.started_at is not None
            and self.expires_at is not None
            and self.started_at <= now < self.expires_at
        )

    def mark_expired_if_needed(self):

        if (
            self.status == self.Status.ACTIVE
            and self.expires_at is not None
            and self.expires_at <= timezone.now()
        ):

            self.status = self.Status.EXPIRED

            self.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            return True

        return False

    def __str__(self):

        return (
            f"{self.user} - "
            f"{self.plan.name} - "
            f"{self.status}"
        )


class SubscriptionOrder(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="subscription_orders",
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default="UGX",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    subscription = models.OneToOneField(
        Subscription,
        on_delete=models.PROTECT,
        related_name="order",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):

        return (
            f"Order #{self.id} - "
            f"{self.user} - "
            f"{self.plan.name}"
        )