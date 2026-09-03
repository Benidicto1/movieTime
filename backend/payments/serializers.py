from rest_framework import serializers


class SubscriptionPaymentSerializer(
    serializers.Serializer
):
    plan_id = serializers.IntegerField()

    payment_method = serializers.ChoiceField(
        choices=[
            "MTN",
            "AIRTEL",
        ]
    )

    phone_number = serializers.CharField(
        max_length=20
    )
