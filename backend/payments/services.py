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


from django.db import transaction

from .models import Payment


class PaymentVerificationService:

    @staticmethod
    @transaction.atomic
    def mark_success(
        *,
        payment,
        provider_reference=None,
    ):
        if payment.status == "SUCCESS":
            return payment

        if payment.status == "FAILED":
            raise ValueError(
                "A failed payment cannot be "
                "marked successful directly."
            )

        payment.status = "SUCCESS"

        if provider_reference:
            payment.provider_reference = (
                provider_reference
            )

        payment.save(
            update_fields=[
                "status",
                "provider_reference",
                "updated_at",
            ]
        )

        return payment


        @staticmethod
        @transaction.atomic
        def mark_failed(
            *,
            payment,
            provider_reference=None,
        ):
            if payment.status == "SUCCESS":
                raise ValueError(
                    "A successful payment cannot "
                    "be marked failed."
                )

            if payment.status == "FAILED":
                return payment

            payment.status = "FAILED"

            if provider_reference:
                payment.provider_reference = (
                    provider_reference
                )

            payment.save(
                update_fields=[
                    "status",
                    "provider_reference",
                    "updated_at",
                ]
            )

            return payment