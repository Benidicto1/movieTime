from rest_framework import serializers

from .models import Purchase


class PurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Purchase

        fields = [
            "id",
            "movie",
            "amount",
            "currency",
            "status",
            "created_at",
            "paid_at",
        ]

        read_only_fields = [
            "id",
            "amount",
            "currency",
            "status",
            "created_at",
            "paid_at",
        ]