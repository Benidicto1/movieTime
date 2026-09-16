# backend/payments/services.py

import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from purchases.models import Purchase
from subscriptions.models import SubscriptionOrder
from subscriptions.services import SubscriptionService

from .exceptions import (
    PaymentAlreadyCompletedError,
    PaymentAlreadyFailedError,
    PaymentCancelledError,
    PaymentConfigurationError,
    PaymentCurrencyMismatchError,
    PaymentError,
    PaymentNotFoundError,
    PaymentProviderError,
    PaymentReferenceError,
    PaymentStateError,
    PaymentVerificationError,
)
from .models import Payment
from .provider_result import (
    PaymentInitiationResult,
    PaymentVerificationResult,
)
from .providers.airtel import AirtelProvider
from .providers.base import MobileMoneyProvider
from .providers.mtn import MTNProvider


class PaymentProviderFactory:
    """
    Creates the correct mobile-money provider implementation.

    Supported providers:
        - MTN
        - AIRTEL
    """

    PROVIDERS = {
        Payment.Provider.MTN: MTNProvider,
        Payment.Provider.AIRTEL: AirtelProvider,
    }

    @classmethod
    def get_provider(cls, provider: str) -> MobileMoneyProvider:
        """
        Return the configured provider implementation.
        """

        normalized_provider = provider.upper().strip()

        provider_class = cls.PROVIDERS.get(
            normalized_provider
        )

        if provider_class is None:
            raise PaymentConfigurationError(
                f"Unsupported payment provider: {provider}"
            )

        try:
            return provider_class()
        except Exception as error:
            raise PaymentConfigurationError(
                "Payment provider is not configured correctly."
            ) from error


class PaymentService:
    """
    Main service responsible for creating and initiating payments.

    Important security rules:

        1. The client does not determine the payment amount.
        2. The client does not determine the payment currency.
        3. The payment must belong to the authenticated user.
        4. A payment must target exactly one Purchase or
           SubscriptionOrder.
        5. A client cannot mark a payment SUCCESS.
        6. Provider success must be independently verified.
    """

    VALID_PROVIDERS = {
        Payment.Provider.MTN,
        Payment.Provider.AIRTEL,
    }

    @staticmethod
    def _generate_external_reference() -> str:
        """
        Generate a unique MovieTime payment reference.
        """

        return f"MT-{uuid.uuid4().hex.upper()}"

    @classmethod
    @transaction.atomic
    def create_payment(
        cls,
        *,
        user,
        provider: str,
        purchase: Purchase | None = None,
        order: SubscriptionOrder | None = None,
    ) -> Payment:
        """
        Create a payment for exactly one target.

        Either:
            purchase
        OR:
            order

        must be provided.

        The amount and currency are always taken from the
        backend object.
        """

        normalized_provider = provider.upper().strip()

        if normalized_provider not in cls.VALID_PROVIDERS:
            raise PaymentConfigurationError(
                f"Unsupported payment provider: {provider}"
            )

        # Exactly one payment target is required.
        if (purchase is None and order is None) or (
            purchase is not None and order is not None
        ):
            raise PaymentError(
                "Payment must target exactly one purchase or subscription order."
            )

        if purchase is not None:
            return cls._create_purchase_payment(
                user=user,
                provider=normalized_provider,
                purchase=purchase,
            )

        return cls._create_subscription_payment(
            user=user,
            provider=normalized_provider,
            order=order,
        )

    @classmethod
    def _create_purchase_payment(
        cls,
        *,
        user,
        provider: str,
        purchase: Purchase,
    ) -> Payment:
        """
        Create a payment for a permanent movie purchase.
        """

        if purchase.user_id != user.id:
            raise PaymentError(
                "You do not have permission to pay for this purchase."
            )

        if purchase.status == Purchase.Status.PAID:
            raise PaymentAlreadyCompletedError(
                "This purchase has already been paid."
            )

        if purchase.status != Purchase.Status.PENDING:
            raise PaymentStateError(
                "This purchase is not available for payment."
            )

        # Reuse an existing active payment instead of creating
        # duplicate provider transactions.
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
            .order_by("-created_at")
            .first()
        )

        if existing_payment is not None:

            # Make sure the payment provider is consistent.
            if existing_payment.provider != provider:
                raise PaymentStateError(
                    "An active payment already exists using another provider."
                )

            return existing_payment

        return Payment.objects.create(
            user=user,
            purchase=purchase,
            order=None,
            provider=provider,
            amount=purchase.amount,
            currency=purchase.currency,
            status=Payment.Status.PENDING,
            external_reference=cls._generate_external_reference(),
        )

    @classmethod
    def _create_subscription_payment(
        cls,
        *,
        user,
        provider: str,
        order: SubscriptionOrder,
    ) -> Payment:
        """
        Create a payment for a subscription order.
        """

        if order.user_id != user.id:
            raise PaymentError(
                "You do not have permission to pay for this subscription order."
            )

        if order.status == SubscriptionOrder.Status.PAID:
            raise PaymentAlreadyCompletedError(
                "This subscription order has already been paid."
            )

        if order.status != SubscriptionOrder.Status.PENDING:
            raise PaymentStateError(
                "This subscription order is not available for payment."
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
            .order_by("-created_at")
            .first()
        )

        if existing_payment is not None:

            if existing_payment.provider != provider:
                raise PaymentStateError(
                    "An active payment already exists using another provider."
                )

            return existing_payment

        return Payment.objects.create(
            user=user,
            purchase=None,
            order=order,
            provider=provider,
            amount=order.amount,
            currency=order.currency,
            status=Payment.Status.PENDING,
            external_reference=cls._generate_external_reference(),
        )

    @classmethod
    @transaction.atomic
    def initiate_mobile_money_payment(
        cls,
        *,
        payment: Payment,
        phone_number: str,
    ) -> Payment:
        """
        Submit a payment to MTN or Airtel.

        IMPORTANT:

        Initiating a mobile-money payment does NOT mean the
        payment succeeded.

        The payment normally becomes PROCESSING until the
        provider confirms the transaction.
        """

        locked_payment = (
            Payment.objects
            .select_for_update()
            .select_related(
                "purchase",
                "order",
                "user",
            )
            .get(pk=payment.pk)
        )

        if locked_payment.status == Payment.Status.SUCCESS:
            raise PaymentAlreadyCompletedError(
                "This payment has already been completed."
            )

        if locked_payment.status == Payment.Status.FAILED:
            raise PaymentAlreadyFailedError(
                "This payment has already failed."
            )

        if locked_payment.status == Payment.Status.CANCELLED:
            raise PaymentCancelledError(
                "This payment has been cancelled."
            )

        if locked_payment.status == Payment.Status.PROCESSING:
            return locked_payment

        if locked_payment.status != Payment.Status.PENDING:
            raise PaymentStateError(
                "Payment cannot be initiated from its current state."
            )

        if not phone_number:
            raise PaymentError(
                "A mobile-money phone number is required."
            )

        try:
            provider = PaymentProviderFactory.get_provider(
                locked_payment.provider
            )

            result = provider.initiate_payment(
                payment=locked_payment,
                phone_number=phone_number,
            )

        except PaymentError:
            raise

        except Exception as error:
            locked_payment.status = Payment.Status.FAILED
            locked_payment.failure_reason = (
                "Payment provider initiation failed."
            )
            locked_payment.completed_at = timezone.now()
            locked_payment.save(
                update_fields=[
                    "status",
                    "failure_reason",
                    "completed_at",
                    "updated_at",
                ]
            )

            raise PaymentProviderError(
                "Unable to initiate payment with the payment provider."
            ) from error

        if not isinstance(result, PaymentInitiationResult):
            locked_payment.status = Payment.Status.FAILED
            locked_payment.failure_reason = (
                "Invalid response from payment provider."
            )
            locked_payment.completed_at = timezone.now()
            locked_payment.save(
                update_fields=[
                    "status",
                    "failure_reason",
                    "completed_at",
                    "updated_at",
                ]
            )

            raise PaymentProviderError(
                "Payment provider returned an invalid response."
            )

        if not result.provider_reference:
            locked_payment.status = Payment.Status.FAILED
            locked_payment.failure_reason = (
                "Payment provider did not return a transaction reference."
            )
            locked_payment.completed_at = timezone.now()
            locked_payment.save(
                update_fields=[
                    "status",
                    "failure_reason",
                    "completed_at",
                    "updated_at",
                ]
            )

            raise PaymentProviderError(
                "Payment provider did not return a valid reference."
            )

        locked_payment.provider_reference = (
            result.provider_reference
        )

        locked_payment.status = cls._map_initiation_status(
            result.status
        )

        locked_payment.failure_reason = ""

        locked_payment.save(
            update_fields=[
                "provider_reference",
                "status",
                "failure_reason",
                "updated_at",
            ]
        )

        return locked_payment

    @staticmethod
    def _map_initiation_status(
        provider_status: str,
    ) -> str:
        """
        Convert provider initiation status into a MovieTime
        payment state.

        Provider initiation success is normally PROCESSING,
        not SUCCESS.
        """

        normalized_status = (
            provider_status or ""
        ).strip().upper()

        if normalized_status in {
            "FAILED",
            "FAILURE",
            "REJECTED",
        }:
            return Payment.Status.FAILED

        if normalized_status in {
            "CANCELLED",
            "CANCELED",
        }:
            return Payment.Status.CANCELLED

        # Do not trust initiation as final success.
        return Payment.Status.PROCESSING


class PaymentVerificationService:
    """
    Handles trusted payment-provider verification.

    This is the only service that should transition a payment
    from PROCESSING to SUCCESS.

    The Android application must never call a client-facing
    endpoint that directly marks a payment successful.
    """

    @classmethod
    @transaction.atomic
    def verify_and_complete(
        cls,
        *,
        payment_id: int,
        verification: PaymentVerificationResult,
    ) -> Payment:
        """
        Verify provider information and complete the payment.

        Verification checks:

            1. Payment exists.
            2. Payment is not already terminal.
            3. Provider reference exists.
            4. Provider reference matches.
            5. Amount matches.
            6. Currency matches.
            7. Provider status represents success.
            8. Purchase/order is still payable.
            9. Target object is updated atomically.
        """

        try:
            payment = (
                Payment.objects
                .select_for_update()
                .select_related(
                    "purchase",
                    "order",
                    "user",
                )
                .get(pk=payment_id)
            )
        except Payment.DoesNotExist as error:
            raise PaymentNotFoundError() from error

        # Idempotency:
        #
        # If the same successful callback is received twice,
        # do not create another purchase/subscription.
        if payment.status == Payment.Status.SUCCESS:

            if (
                verification.provider_reference
                and payment.provider_reference
                == verification.provider_reference
            ):
                return payment

            raise PaymentAlreadyCompletedError(
                "Payment has already been completed."
            )

        if payment.status == Payment.Status.FAILED:
            raise PaymentAlreadyFailedError(
                "Payment has already failed."
            )

        if payment.status == Payment.Status.CANCELLED:
            raise PaymentCancelledError(
                "Payment has been cancelled."
            )

        if payment.status not in {
            Payment.Status.PENDING,
            Payment.Status.PROCESSING,
        }:
            raise PaymentStateError(
                "Payment cannot be verified from its current state."
            )

        if not payment.provider_reference:
            raise PaymentReferenceError(
                "Payment does not have a provider reference."
            )

        if not verification.provider_reference:
            raise PaymentReferenceError(
                "Provider verification did not return a reference."
            )

        if (
            payment.provider_reference
            != verification.provider_reference
        ):
            raise PaymentReferenceError(
                "Provider reference does not match the payment."
            )

        expected_amount = Decimal(payment.amount)
        verified_amount = Decimal(verification.amount)

        if expected_amount != verified_amount:
            raise PaymentVerificationError(
                "Payment amount does not match the expected amount."
            )

        if (
            payment.currency.upper()
            != verification.currency.upper()
        ):
            raise PaymentVerificationError(
                "Payment currency does not match the expected currency."
            )

        if not cls._is_success_status(
            verification.status
        ):
            raise PaymentVerificationError(
                "Payment provider has not confirmed successful payment."
            )

        cls._check_duplicate_provider_reference(
            payment=payment,
            provider_reference=verification.provider_reference,
        )

        # Complete payment.
        payment.status = Payment.Status.SUCCESS
        payment.completed_at = timezone.now()
        payment.failure_reason = ""

        payment.save(
            update_fields=[
                "status",
                "completed_at",
                "failure_reason",
                "updated_at",
            ]
        )

        # Update exactly one payment target.
        if payment.purchase_id is not None:
            cls._complete_purchase(payment)

        elif payment.order_id is not None:
            cls._complete_subscription_order(payment)

        else:
            raise PaymentVerificationError(
                "Payment does not have a valid payment target."
            )

        return payment

    @staticmethod
    def _is_success_status(
        provider_status: str,
    ) -> bool:
        """
        Determine whether the provider's verification result
        represents successful payment.

        Provider-specific implementations may normalize their
        response before creating PaymentVerificationResult.
        """

        return (
            provider_status or ""
        ).strip().upper() in {
            "SUCCESS",
            "SUCCESSFUL",
            "COMPLETED",
            "PAID",
        }

    @staticmethod
    def _check_duplicate_provider_reference(
        *,
        payment: Payment,
        provider_reference: str,
    ) -> None:
        """
        Prevent a provider transaction reference from being
        associated with another MovieTime payment.
        """

        duplicate = (
            Payment.objects
            .filter(
                provider=payment.provider,
                provider_reference=provider_reference,
            )
            .exclude(pk=payment.pk)
            .first()
        )

        if duplicate is not None:
            raise PaymentReferenceError(
                "Provider reference is already associated with another payment."
            )

    @staticmethod
    def _complete_purchase(
        payment: Payment,
    ) -> None:
        """
        Mark the permanent movie purchase as PAID.

        This happens only after trusted payment verification.
        """

        purchase = (
            Purchase.objects
            .select_for_update()
            .get(pk=payment.purchase_id)
        )

        if purchase.user_id != payment.user_id:
            raise PaymentVerificationError(
                "Payment user does not match purchase owner."
            )

        if purchase.status == Purchase.Status.PAID:
            return

        if purchase.status != Purchase.Status.PENDING:
            raise PaymentVerificationError(
                "Purchase cannot be completed from its current state."
            )

        if Decimal(purchase.amount) != Decimal(payment.amount):
            raise PaymentVerificationError(
                "Purchase amount does not match payment amount."
            )

        if (
            purchase.currency.upper()
            != payment.currency.upper()
        ):
            raise PaymentVerificationError(
                "Purchase currency does not match payment currency."
            )

        purchase.status = Purchase.Status.PAID
        purchase.paid_at = timezone.now()

        purchase.save(
            update_fields=[
                "status",
                "paid_at",
                "updated_at",
            ]
        )

    @staticmethod
    def _complete_subscription_order(
        payment: Payment,
    ) -> None:
        """
        Mark the subscription order as PAID and activate the
        associated subscription.

        SubscriptionService is responsible for subscription
        activation.
        """

        order = (
            SubscriptionOrder.objects
            .select_for_update()
            .select_related(
                "plan",
                "user",
            )
            .get(pk=payment.order_id)
        )

        if order.user_id != payment.user_id:
            raise PaymentVerificationError(
                "Payment user does not match subscription owner."
            )

        if order.status == SubscriptionOrder.Status.PAID:
            # Idempotent behavior.
            SubscriptionService.activate_subscription(
                order=order
            )
            return

        if order.status != SubscriptionOrder.Status.PENDING:
            raise PaymentVerificationError(
                "Subscription order cannot be completed from its current state."
            )

        if Decimal(order.amount) != Decimal(payment.amount):
            raise PaymentVerificationError(
                "Subscription order amount does not match payment amount."
            )

        if (
            order.currency.upper()
            != payment.currency.upper()
        ):
            raise PaymentVerificationError(
                "Subscription order currency does not match payment currency."
            )

        order.status = SubscriptionOrder.Status.PAID

        order.save(
            update_fields=[
                "status",
            ]
        )

        SubscriptionService.activate_subscription(
            order=order
        )

    @classmethod
    @transaction.atomic
    def mark_failed(
        cls,
        *,
        payment_id: int,
        reason: str = "Payment failed.",
    ) -> Payment:
        """
        Mark a payment as FAILED.

        This method is intended for trusted backend/provider
        processing, not direct Android requests.
        """

        try:
            payment = (
                Payment.objects
                .select_for_update()
                .get(pk=payment_id)
            )
        except Payment.DoesNotExist as error:
            raise PaymentNotFoundError() from error

        if payment.status == Payment.Status.SUCCESS:
            raise PaymentAlreadyCompletedError(
                "A successful payment cannot be marked as failed."
            )

        if payment.status == Payment.Status.CANCELLED:
            raise PaymentCancelledError(
                "A cancelled payment cannot be marked as failed."
            )

        payment.status = Payment.Status.FAILED
        payment.failure_reason = reason
        payment.completed_at = timezone.now()

        payment.save(
            update_fields=[
                "status",
                "failure_reason",
                "completed_at",
                "updated_at",
            ]
        )

        return payment

    @classmethod
    @transaction.atomic
    def mark_cancelled(
        cls,
        *,
        payment_id: int,
        reason: str = "Payment was cancelled.",
    ) -> Payment:
        """
        Mark a payment as cancelled.

        This should be called only by trusted backend logic.
        """

        try:
            payment = (
                Payment.objects
                .select_for_update()
                .get(pk=payment_id)
            )
        except Payment.DoesNotExist as error:
            raise PaymentNotFoundError() from error

        if payment.status == Payment.Status.SUCCESS:
            raise PaymentAlreadyCompletedError(
                "A successful payment cannot be cancelled."
            )

        if payment.status == Payment.Status.FAILED:
            raise PaymentAlreadyFailedError(
                "A failed payment cannot be cancelled."
            )

        payment.status = Payment.Status.CANCELLED
        payment.failure_reason = reason
        payment.completed_at = timezone.now()

        payment.save(
            update_fields=[
                "status",
                "failure_reason",
                "completed_at",
                "updated_at",
            ]
        )

        return payment