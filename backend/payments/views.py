from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.abuse_prevention import (
    AbusePreventionService,
    InvalidOperationError,
)
from config.throttling import (
    PaymentRateThrottle,
    PaymentStatusRateThrottle,
)

from payments.models import Payment
from payments.services import (
    PaymentService,
    PaymentVerificationService,
)

from purchases.models import Purchase
from subscriptions.models import SubscriptionOrder


class PurchasePaymentAPIView(APIView):
    """
    Create a mobile-money payment for an existing purchase.

    POST /api/v1/payments/purchases/

    Expected JSON:
    {
        "purchase_id": 1,
        "provider": "mtn",
        "phone_number": "0771234567"
    }
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentRateThrottle]

    def post(self, request):
        try:
            purchase_id = AbusePreventionService.normalize_identifier(
                request.data.get("purchase_id")
            )

            provider = str(
                request.data.get("provider", "")
            ).strip().upper()

            phone_number = str(
                request.data.get("phone_number", "")
            ).strip()

            if not provider:
                raise InvalidOperationError(
                    "Payment provider is required."
                )

            if provider not in (
                Payment.Provider.MTN,
                Payment.Provider.AIRTEL,
            ):
                raise InvalidOperationError(
                    "Unsupported payment provider."
                )

            if not phone_number:
                raise InvalidOperationError(
                    "Phone number is required."
                )

            try:
                purchase = Purchase.objects.get(
                    id=int(purchase_id),
                    user=request.user,
                )
            except (Purchase.DoesNotExist, ValueError):
                return Response(
                    {
                        "detail": "Purchase not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            payment = PaymentService.create_payment(
                user=request.user,
                provider=provider,
                purchase=purchase,
            )

            initiation = PaymentService.initiate_mobile_money_payment(
                payment=payment,
                phone_number=phone_number,
            )

            return Response(
                {
                    "id": payment.id,
                    "external_reference": payment.external_reference,
                    "provider": payment.provider,
                    "amount": str(payment.amount),
                    "currency": payment.currency,
                    "status": payment.status,
                    "provider_reference": (
                        initiation.provider_reference
                    ),
                    "message": initiation.message,
                },
                status=status.HTTP_201_CREATED,
            )

        except InvalidOperationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SubscriptionPaymentAPIView(APIView):
    """
    Create a mobile-money payment for a subscription order.

    POST /api/v1/payments/subscriptions/

    Expected JSON:
    {
        "order_id": 1,
        "provider": "mtn",
        "phone_number": "0771234567"
    }
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentRateThrottle]

    def post(self, request):
        try:
            order_id = AbusePreventionService.normalize_identifier(
                request.data.get("order_id")
            )

            provider = str(
                request.data.get("provider", "")
            ).strip().upper()

            phone_number = str(
                request.data.get("phone_number", "")
            ).strip()

            if not provider:
                raise InvalidOperationError(
                    "Payment provider is required."
                )

            if provider not in (
                Payment.Provider.MTN,
                Payment.Provider.AIRTEL,
            ):
                raise InvalidOperationError(
                    "Unsupported payment provider."
                )

            if not phone_number:
                raise InvalidOperationError(
                    "Phone number is required."
                )

            try:
                order = SubscriptionOrder.objects.select_related(
                    "subscription"
                ).get(
                    id=int(order_id),
                    user=request.user,
                )
            except (SubscriptionOrder.DoesNotExist, ValueError):
                return Response(
                    {
                        "detail": "Subscription order not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            payment = PaymentService.create_payment(
                user=request.user,
                provider=provider,
                order=order,
            )

            initiation = PaymentService.initiate_mobile_money_payment(
                payment=payment,
                phone_number=phone_number,
            )

            return Response(
                {
                    "id": payment.id,
                    "external_reference": payment.external_reference,
                    "provider": payment.provider,
                    "amount": str(payment.amount),
                    "currency": payment.currency,
                    "status": payment.status,
                    "provider_reference": (
                        initiation.provider_reference
                    ),
                    "message": initiation.message,
                },
                status=status.HTTP_201_CREATED,
            )

        except InvalidOperationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentStatusAPIView(APIView):
    """
    Return the current payment status.

    GET /api/v1/payments/<payment_id>/status/
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentStatusRateThrottle]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(
                id=payment_id,
                user=request.user,
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "detail": "Payment not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "id": payment.id,
                "external_reference": payment.external_reference,
                "provider": payment.provider,
                "amount": str(payment.amount),
                "currency": payment.currency,
                "status": payment.status,
                "provider_reference": payment.provider_reference,
                "target_type": payment.target_type,
                "target_id": payment.target_id,
                "created_at": payment.created_at,
                "completed_at": payment.completed_at,
            },
            status=status.HTTP_200_OK,
        )


class PaymentVerificationAPIView(APIView):
    """
    Verify a payment with the configured mobile-money provider.

    IMPORTANT:
    This endpoint is intended for backend-side verification.
    The Android client must never be treated as the authority
    for payment success.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [PaymentRateThrottle]

    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(
                id=payment_id,
                user=request.user,
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "detail": "Payment not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            verification = PaymentService.verify_payment(
                payment=payment,
            )

            completed_payment = (
                PaymentVerificationService.verify_and_complete(
                    payment_id=payment.id,
                    verification=verification,
                )
            )

            return Response(
                {
                    "id": completed_payment.id,
                    "status": completed_payment.status,
                    "provider": completed_payment.provider,
                    "amount": str(completed_payment.amount),
                    "currency": completed_payment.currency,
                    "provider_reference": (
                        completed_payment.provider_reference
                    ),
                    "completed_at": completed_payment.completed_at,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )