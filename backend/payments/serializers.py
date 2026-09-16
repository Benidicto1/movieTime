# backend/payments/serializers.py

from rest_framework import serializers

from payments.models import Payment
from payments.validators import validate_uganda_phone_number


class PurchasePaymentSerializer(serializers.Serializer):
    """
    Serializer for initiating a payment for an existing movie purchase.

    The backend determines the payment amount from the Purchase record.
    The client must never be trusted to provide the amount.
    """

    purchase_id = serializers.IntegerField(
        min_value=1,
    )

    payment_method = serializers.ChoiceField(
        choices=[
            Payment.Provider.MTN,
            Payment.Provider.AIRTEL,
        ],
    )

    phone_number = serializers.CharField(
        max_length=12,
        write_only=True,
        validators=[validate_uganda_phone_number],
    )


class SubscriptionPaymentSerializer(serializers.Serializer):
    """
    Serializer for initiating a subscription payment.

    The backend determines the subscription price from the
    SubscriptionPlan record.
    """

    plan_id = serializers.IntegerField(
        min_value=1,
    )

    payment_method = serializers.ChoiceField(
        choices=[
            Payment.Provider.MTN,
            Payment.Provider.AIRTEL,
        ],
    )

    phone_number = serializers.CharField(
        max_length=12,
        write_only=True,
        validators=[validate_uganda_phone_number],
    )


class PaymentCreateResponseSerializer(serializers.ModelSerializer):
    """
    Safe response serializer returned after payment creation.

    Sensitive information such as the customer's phone number
    is deliberately excluded.
    """

    payment_id = serializers.IntegerField(
        source="id",
        read_only=True,
    )

    payment_status = serializers.CharField(
        source="status",
        read_only=True,
    )

    purchase_id = serializers.IntegerField(
        source="purchase_id",
        read_only=True,
    )

    order_id = serializers.IntegerField(
        source="order_id",
        read_only=True,
    )

    message = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "payment_id",
            "amount",
            "currency",
            "provider",
            "payment_status",
            "external_reference",
            "provider_reference",
            "purchase_id",
            "order_id",
            "message",
        ]
        read_only_fields = fields

    def get_message(self, obj):
        if obj.status == Payment.Status.PENDING:
            return (
                "Payment has been created and is waiting "
                "for processing."
            )

        if obj.status == Payment.Status.PROCESSING:
            return (
                "Payment request has been sent. "
                "Waiting for payment confirmation."
            )

        if obj.status == Payment.Status.SUCCESS:
            return "Payment completed successfully."

        if obj.status == Payment.Status.FAILED:
            return "Payment failed."

        if obj.status == Payment.Status.CANCELLED:
            return "Payment was cancelled."

        return "Payment status updated."


class PaymentStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for checking the current status of a payment.

    This endpoint is read-only from the Android application's
    perspective. The client cannot change payment status.
    """

    payment_id = serializers.IntegerField(
        source="id",
        read_only=True,
    )

    payment_method = serializers.CharField(
        source="provider",
        read_only=True,
    )

    purchase_id = serializers.IntegerField(
        source="purchase_id",
        read_only=True,
    )

    order_id = serializers.IntegerField(
        source="order_id",
        read_only=True,
    )

    class Meta:
        model = Payment
        fields = [
            "payment_id",
            "status",
            "amount",
            "currency",
            "payment_method",
            "external_reference",
            "provider_reference",
            "completed_at",
            "purchase_id",
            "order_id",
        ]
        read_only_fields = fields