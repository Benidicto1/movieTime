from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from purchases.models import Purchase
from subscriptions.models import SubscriptionPlan
from subscriptions.services import SubscriptionService

from .models import Payment
from .serializers import (
    PurchasePaymentSerializer,
    SubscriptionPaymentSerializer,
)
from .services import PaymentService


class SubscriptionPaymentAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(
        self,
        request,
    ):
        serializer = (
            SubscriptionPaymentSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        plan_id = (
            serializer.validated_data[
                "plan_id"
            ]
        )

        payment_method = (
            serializer.validated_data[
                "payment_method"
            ]
        )

        phone_number = (
            serializer.validated_data[
                "phone_number"
            ]
        )

        plan = (
            SubscriptionPlan.objects
            .filter(
                id=plan_id,
                is_active=True,
            )
            .first()
        )

        if plan is None:
            return Response(
                {
                    "detail": (
                        "Subscription plan "
                        "not found."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        try:
            order = (
                SubscriptionService
                .create_order(
                    user=request.user,
                    plan_id=plan.id,
                )
            )

            payment = (
                PaymentService
                .create_payment(
                    order=order,
                    provider=payment_method,
                )
            )

        except ValueError as error:
            return Response(
                {
                    "detail": str(error)
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        return Response(
            {
                "order_id": order.id,
                "payment_id": payment.id,
                "plan_id": order.plan_id,
                "amount": str(
                    payment.amount
                ),
                "currency": payment.currency,
                "payment_method": (
                    payment.provider
                ),
                "payment_status": (
                    payment.status
                ),
                "external_reference": (
                    payment.external_reference
                ),
                "message": (
                    "Payment created. "
                    "Mobile Money initiation "
                    "will be handled by the "
                    "backend payment provider."
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class PurchasePaymentAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(
        self,
        request,
    ):
        serializer = (
            PurchasePaymentSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        purchase_id = (
            serializer.validated_data[
                "purchase_id"
            ]
        )

        payment_method = (
            serializer.validated_data[
                "payment_method"
            ]
        )

        purchase = (
            Purchase.objects
            .filter(
                id=purchase_id,
                user=request.user,
            )
            .select_related("movie")
            .first()
        )

        if purchase is None:
            return Response(
                {
                    "detail": (
                        "Purchase not found."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        try:
            payment = (
                PaymentService
                .create_payment(
                    purchase=purchase,
                    provider=payment_method,
                )
            )

        except ValueError as error:
            return Response(
                {
                    "detail": str(error)
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        return Response(
            {
                "purchase_id": purchase.id,
                "payment_id": payment.id,
                "movie_id": purchase.movie_id,
                "amount": str(
                    payment.amount
                ),
                "currency": payment.currency,
                "payment_method": (
                    payment.provider
                ),
                "payment_status": (
                    payment.status
                ),
                "external_reference": (
                    payment.external_reference
                ),
                "message": (
                    "Payment created. "
                    "Mobile Money initiation "
                    "will be handled by the "
                    "backend payment provider."
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentStatusAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        payment_id,
    ):
        payment = (
            Payment.objects
            .filter(
                id=payment_id,
                user=request.user,
            )
            .select_related(
                "order",
                "purchase",
            )
            .first()
        )

        if payment is None:
            return Response(
                {
                    "detail": (
                        "Payment not found."
                    )
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        response = {
            "payment_id": payment.id,
            "status": payment.status,
            "amount": str(
                payment.amount
            ),
            "currency": payment.currency,
            "payment_method": payment.provider,
            "external_reference": (
                payment.external_reference
            ),
            "completed_at": (
                payment.completed_at
            ),
        }

        if payment.order_id:
            response[
                "order_id"
            ] = payment.order_id

        if payment.purchase_id:
            response[
                "purchase_id"
            ] = payment.purchase_id

        return Response(
            response,
            status=status.HTTP_200_OK,
        )