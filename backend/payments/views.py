from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    SubscriptionPaymentSerializer,
)

from .services import PaymentService

from subscriptions.models import SubscriptionPlan
from subscriptions.services import SubscriptionService


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
                    "detail":
                        "Subscription plan "
                        "not found."
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

                "payment_method":
                    payment.provider,

                "payment_status":
                    payment.status,

                "external_reference":
                    payment.external_reference,

                "phone_number":
                    phone_number,

                "message":
                    "Payment created. "
                    "Provider initiation "
                    "will be performed "
                    "separately.",
            },
            status=status.HTTP_201_CREATED,
        )