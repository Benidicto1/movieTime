import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from purchases.models import Purchase
from subscriptions.models import SubscriptionOrder
from subscriptions.services import SubscriptionService

from .models import Payment
from .providers.factory import get_payment_provider


class PaymentService:

    @staticmethod
    def generate_reference():
        return (
            "MOVIETIME-"
            f"{uuid.uuid4().hex.upper()}"
        )

    @staticmethod
    @transaction.atomic
    def create_payment(
        *,
        provider,
        order=None,
        purchase=None,
    ):
        if (
            (order is None and purchase is None)
            or
            (order is not None and purchase is not None)
        ):
            raise ValueError(
                "Payment must belong to exactly "
                "one order or purchase."
            )

        provider = provider.upper()

        if provider not in {
            Payment.Provider.MTN,
            Payment.Provider.AIRTEL,
        }:
            raise ValueError(
                "Unsupported payment provider."
            )

        if order is not None:

            if (
                order.status
                != SubscriptionOrder.Status.PENDING
            ):
                raise ValueError(
                    "This subscription order "
                    "cannot receive a payment."
                )

            existing_payment = (
                Payment.objects
                .select_for_update()
                .filter(
                    order=order,
                    status__in=[
                        Payment.Status.PENDING,
                        Payment.Status.PROCESSING,
                    ],
                )
                .first()
            )

            if existing_payment:
                return existing_payment

            user = order.user
            amount = order.amount
            currency = order.currency

        else:

            if (
                purchase.status
                != Purchase.Status.PENDING
            ):
                raise ValueError(
                    "This purchase cannot "
                    "receive a payment."
                )

            existing_payment = (
                Payment.objects
                .select_for_update()
                .filter(
                    purchase=purchase,
                    status__in=[
                        Payment.Status.PENDING,
                        Payment.Status.PROCESSING,
                    ],
                )
                .first()
            )

            if existing_payment:
                return existing_payment

            user = purchase.user
            amount = purchase.amount
            currency = purchase.currency

        return Payment.objects.create(
            order=order,
            purchase=purchase,
            user=user,
            provider=provider,
            amount=amount,
            currency=currency,
            status=Payment.Status.PENDING,
            external_reference=(
                PaymentService
                .generate_reference()
            ),
        )

    @staticmethod
    @transaction.atomic
    def initiate_mobile_money_payment(
        *,
        payment,
        phone_number,
    ):
        payment = (
            Payment.objects
            .select_for_update()
            .get(
                pk=payment.pk
            )
        )

        if payment.status not in {
            Payment.Status.PENDING,
        }:
            raise ValueError(
                "Only pending payments "
                "can be initiated."
            )

        provider = get_payment_provider(
            payment.provider
        )

        result = (
            provider
            .initiate_payment(
                amount=payment.amount,
                currency=payment.currency,
                phone_number=phone_number,
                reference=(
                    payment.external_reference
                ),
            )
        )

        payment.status = (
            Payment.Status.PROCESSING
        )

        payment.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return result


class PaymentVerificationService:

    @staticmethod
    @transaction.atomic
    def mark_success(
        *,
        payment,
        provider_reference,
        verified_amount,
        verified_currency,
    ):
        payment = (
            Payment.objects
            .select_for_update()
            .select_related(
                "order",
                "purchase",
            )
            .get(
                pk=payment.pk
            )
        )

        if (
            payment.status
            == Payment.Status.SUCCESS
        ):
            return payment

        if payment.status in {
            Payment.Status.FAILED,
            Payment.Status.CANCELLED,
        }:
            raise ValueError(
                "This payment cannot be "
                "marked successful."
            )

        if not provider_reference:
            raise ValueError(
                "A provider reference is "
                "required."
            )

        verified_amount = Decimal(
            str(verified_amount)
        )

        verified_currency = (
            str(verified_currency)
            .upper()
        )

        if verified_amount != payment.amount:
            raise ValueError(
                "Verified payment amount "
                "does not match the "
                "MovieTime payment."
            )

        if verified_currency != payment.currency:
            raise ValueError(
                "Verified payment currency "
                "does not match the "
                "MovieTime payment."
            )

        reference_exists = (
            Payment.objects
            .exclude(
                pk=payment.pk
            )
            .filter(
                provider_reference=(
                    provider_reference
                )
            )
            .exists()
        )

        if reference_exists:
            raise ValueError(
                "Provider reference is "
                "already associated with "
                "another payment."
            )

        now = timezone.now()

        payment.status = (
            Payment.Status.SUCCESS
        )

        payment.provider_reference = (
            provider_reference
        )

        payment.completed_at = now

        payment.save(
            update_fields=[
                "status",
                "provider_reference",
                "completed_at",
                "updated_at",
            ]
        )

        if payment.order is not None:

            order = (
                SubscriptionOrder.objects
                .select_for_update()
                .get(
                    pk=payment.order_id
                )
            )

            if (
                order.status
                != SubscriptionOrder.Status.PAID
            ):
                order.status = (
                    SubscriptionOrder.Status.PAID
                )

                order.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

            SubscriptionService.activate_subscription(
                order=order
            )

        elif payment.purchase is not None:

            purchase = (
                Purchase.objects
                .select_for_update()
                .get(
                    pk=payment.purchase_id
                )
            )

            if (
                purchase.status
                != Purchase.Status.PAID
            ):
                purchase.status = (
                    Purchase.Status.PAID
                )

                purchase.paid_at = now

                purchase.save(
                    update_fields=[
                        "status",
                        "paid_at",
                        "updated_at",
                    ]
                )

        else:
            raise ValueError(
                "Payment has no valid "
                "financial target."
            )

        return payment

    @staticmethod
    @transaction.atomic
    def mark_failed(
        *,
        payment,
        provider_reference=None,
        failure_reason=None,
    ):
        payment = (
            Payment.objects
            .select_for_update()
            .get(
                pk=payment.pk
            )
        )

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

        if failure_reason:
            payment.failure_reason = (
                failure_reason
            )

        payment.completed_at = (
            timezone.now()
        )

        payment.save(
            update_fields=[
                "status",
                "provider_reference",
                "failure_reason",
                "completed_at",
                "updated_at",
            ]
        )

        return payment