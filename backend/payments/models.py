# backend/payments/models.py

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q

from purchases.models import Purchase
from subscriptions.models import SubscriptionOrder


class Payment(models.Model):
    """
    Represents a MovieTime mobile-money payment.

    A payment must belong to exactly ONE payment target:

        1. A Purchase
        OR
        2. A SubscriptionOrder

    The backend is authoritative for:
        - amount
        - currency
        - payment status
        - provider reference
        - ownership
        - payment completion

    The Android application must never directly mark a payment
    as SUCCESS.
    """

    class Provider(models.TextChoices):
        MTN = "MTN", "MTN Mobile Money"
        AIRTEL = "AIRTEL", "Airtel Money"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    # Subscription payment target.
    #
    # Nullable because a payment can instead belong to a
    # permanent movie Purchase.
    order = models.ForeignKey(
        SubscriptionOrder,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments",
    )

    # Permanent movie purchase payment target.
    #
    # Nullable because a payment can instead belong to a
    # SubscriptionOrder.
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments",
    )

    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
    )

    amount = models.DecimalField(
        max_digits=12,
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

    # MovieTime-generated reference.
    #
    # This is NOT the same as the provider's transaction reference.
    external_reference = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
    )

    # Reference returned by MTN/Airtel.
    #
    # Nullable because the provider reference may not exist
    # immediately after payment creation.
    provider_reference = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
    )

    failure_reason = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            # Every payment must target exactly ONE thing:
            #
            # order != NULL and purchase == NULL
            #
            # OR
            #
            # order == NULL and purchase != NULL
            models.CheckConstraint(
                condition=(
                    (
                        Q(order__isnull=False)
                        & Q(purchase__isnull=True)
                    )
                    |
                    (
                        Q(order__isnull=True)
                        & Q(purchase__isnull=False)
                    )
                ),
                name="payment_exactly_one_target",
            ),

            # Prevent multiple active payments for the same
            # subscription order.
            models.UniqueConstraint(
                fields=["order"],
                condition=(
                    Q(order__isnull=False)
                    & Q(
                        status__in=[
                            "PENDING",
                            "PROCESSING",
                        ]
                    )
                ),
                name="one_active_payment_per_order",
            ),

            # Prevent multiple active payments for the same
            # permanent movie purchase.
            models.UniqueConstraint(
                fields=["purchase"],
                condition=(
                    Q(purchase__isnull=False)
                    & Q(
                        status__in=[
                            "PENDING",
                            "PROCESSING",
                        ]
                    )
                ),
                name="one_active_payment_per_purchase",
            ),
        ]

    def save(self, *args, **kwargs):
        """
        Generate a MovieTime external reference when creating
        a new payment.

        Existing references are preserved.
        """

        if not self.external_reference:
            self.external_reference = (
                f"MT-{uuid.uuid4().hex.upper()}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        target = (
            f"Purchase #{self.purchase_id}"
            if self.purchase_id
            else f"Subscription Order #{self.order_id}"
        )

        return (
            f"{self.external_reference} - "
            f"{self.provider} - "
            f"{target} - "
            f"{self.status}"
        )

    @property
    def is_pending(self):
        """
        Return True when the payment is waiting to be processed.
        """
        return self.status == self.Status.PENDING

    @property
    def is_processing(self):
        """
        Return True when the payment has been submitted to the
        provider and final confirmation is still pending.
        """
        return self.status == self.Status.PROCESSING

    @property
    def is_successful(self):
        """
        Return True only when the backend has established that
        the payment was successfully completed.
        """
        return self.status == self.Status.SUCCESS

    @property
    def is_failed(self):
        """
        Return True when payment processing failed.
        """
        return self.status == self.Status.FAILED

    @property
    def is_cancelled(self):
        """
        Return True when the payment was cancelled.
        """
        return self.status == self.Status.CANCELLED

    @property
    def target_type(self):
        """
        Return the type of object this payment targets.
        """

        if self.purchase_id is not None:
            return "purchase"

        if self.order_id is not None:
            return "subscription"

        return None

    @property
    def target_id(self):
        """
        Return the ID of the object this payment targets.
        """

        if self.purchase_id is not None:
            return self.purchase_id

        if self.order_id is not None:
            return self.order_id

        return None