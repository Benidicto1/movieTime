import uuid

from django.db import transaction
from django.utils import timezone

from .models import Payment
from subscriptions.models import SubscriptionOrder


class PaymentService:
    """
    Handles creation of MovieTime payment records.
    """

    @staticmethod
    def generate_reference():
        return f"MOVIETIME-{uuid.uuid4().hex.upper()}"

    @staticmethod
    @transaction.atomic
    def create_payment(
        *,
        order,
        provider,
    ):
        """
        Create a payment for a pending subscription order.
        """

        if order.status != SubscriptionOrder.Status.PENDING:
            raise ValueError(
                "This order cannot receive a payment."
            )

        payment = Payment.objects.create(
            order=order,
            user=order.user,
            provider=provider,
            amount=order.amount,
            currency=order.currency,
            status=Payment.Status.PENDING,
            external_reference=(
                PaymentService.generate_reference()
            ),
        )

        return payment


class PaymentVerificationService:
    """
    Handles payment verification results.

    IMPORTANT:
    This service should only be called after the
    payment provider has actually confirmed the
    transaction.
    """

    @staticmethod
    @transaction.atomic
    def mark_success(
        *,
        payment,
        provider_reference,
    ):
        """
        Mark a payment as successfully completed.
        """

        payment = (
            Payment.objects
            .select_for_update()
            .select_related(
                "order",
                "order__plan",
            )
            .get(
                pk=payment.pk
            )
        )

        # Prevent duplicate processing
        if payment.status == Payment.Status.SUCCESS:
            return payment

        payment.status = Payment.Status.SUCCESS

        payment.provider_reference = (
            provider_reference
        )

        payment.completed_at = timezone.now()

        payment.save(
            update_fields=[
                "status",
                "provider_reference",
                "completed_at",
                "updated_at",
            ]
        )

        return payment

    @staticmethod
    @transaction.atomic
    def mark_failed(
        *,
        payment,
        failure_reason=None,
    ):
        """
        Mark a payment as failed.
        """

        payment = (
            Payment.objects
            .select_for_update()
            .get(
                pk=payment.pk
            )
        )

        # Don't overwrite a successful payment
        if payment.status == Payment.Status.SUCCESS:
            return payment

        payment.status = Payment.Status.FAILED

        payment.failure_reason = (
            failure_reason
        )

        payment.save(
            update_fields=[
                "status",
                "failure_reason",
                "updated_at",
            ]
        )

        return payment