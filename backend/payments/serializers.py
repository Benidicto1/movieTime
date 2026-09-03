from rest_framework import serializers

from .validators import (
    validate_uganda_phone_number,
)


class SubscriptionPaymentSerializer(
    serializers.Serializer
):

    plan_id = serializers.IntegerField(
        min_value=1
    )

    payment_method = (
        serializers.ChoiceField(
            choices=[
                "MTN",
                "AIRTEL",
            ]
        )
    )

    phone_number = serializers.CharField(
        max_length=20,
        trim_whitespace=True,
    )

    def validate_phone_number(
        self,
        value,
    ):
        try:
            return validate_uganda_phone_number(
                value
            )
        except ValueError as error:
            raise serializers.ValidationError(
                str(error)
            )


class PurchasePaymentSerializer(
    serializers.Serializer
):

    purchase_id = serializers.IntegerField(
        min_value=1
    )

    payment_method = (
        serializers.ChoiceField(
            choices=[
                "MTN",
                "AIRTEL",
            ]
        )
    )

    phone_number = serializers.CharField(
        max_length=20,
        trim_whitespace=True,
    )

    def validate_phone_number(
        self,
        value,
    ):
        try:
            return validate_uganda_phone_number(
                value
            )
        except ValueError as error:
            raise serializers.ValidationError(
                str(error)
            )