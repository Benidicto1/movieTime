from django.conf import settings
from django.db import models

from subscriptions.models import SubscriptionOrder


class Payment(models.Model):

    class Provider(models.TextChoices):
        MTN = "MTN", "MTN Mobile Money"
        AIRTEL = "AIRTEL", "Airtel Money"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    order = models.ForeignKey(
        SubscriptionOrder,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
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

    provider_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
    )

    external_reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
    )

    failure_reason = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return (
            f"Payment #{self.id} - "
            f"{self.provider} - "
            f"{self.status}"
        )