import uuid

from django.db import transaction

from .models import Payment
from .providers.factory import get_payment_provider

from subscriptions.models import SubscriptionOrder


class PaymentService:
    """
    Handles creation of MovieTime payment records.
    """

    @staticmethod
    def generate_reference():
        return (
            f"MOVIETIME-"
            f"{uuid.uuid4().hex.upper()}"
        )

    @staticmethod
    @transaction.atomic
    def create_payment(
        *,
        order,
        provider,
    ):
        """
        Create a payment for a pending
        subscription order.
        """

        if (
            order.status
            != SubscriptionOrder.Status.PENDING
        ):
            raise ValueError(
                "This order cannot receive "
                "a payment."
            )

        provider = provider.upper()

        payment = Payment.objects.create(
            order=order,
            user=order.user,
            provider=provider,
            amount=order.amount,
            currency=order.currency,
            status=Payment.Status.PENDING,
            external_reference=(
                PaymentService
                .generate_reference()
            ),
        )

        return payment

    @staticmethod
    @transaction.atomic
    def initiate_mobile_money_payment(
        *,
        payment,
        phone_number,
    ):
        """
        Initiate payment with the selected
        mobile money provider.
        """

        if (
            payment.status
            != Payment.Status.PENDING
        ):
            raise ValueError(
                "Only pending payments "
                "can be initiated."
            )

        provider = get_payment_provider(
            payment.provider
        )

        result = provider.initiate_payment(
            amount=payment.amount,
            currency=payment.currency,
            phone_number=phone_number,
            reference=(
                payment.external_reference
            ),
        )

        return result


class PaymentVerificationService:

    @staticmethod
    @transaction.atomic
    def mark_success(
        *,
        payment,
        provider_reference=None,
    ):
        """
        Mark a pending payment as successful.
        """

        if (
            payment.status
            == Payment.Status.SUCCESS
        ):
            return payment

        if (
            payment.status
            == Payment.Status.FAILED
        ):
            raise ValueError(
                "A failed payment cannot be "
                "marked successful directly."
            )

        payment.status = (
            Payment.Status.SUCCESS
        )

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
        """
        Mark a pending payment as failed.
        """

        if (
            payment.status
            == Payment.Status.SUCCESS
        ):
            raise ValueError(
                "A successful payment cannot "
                "be marked failed."
            )

        if (
            payment.status
            == Payment.Status.FAILED
        ):
            return payment

        payment.status = (
            Payment.Status.FAILED
        )

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
