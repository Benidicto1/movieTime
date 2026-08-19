from rest_framework import serializers

from .models import Download


class DownloadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Download

        fields = [
            "id",
            "movie",
            "status",
            "created_at",
            "completed_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_at",
            "completed_at",
        ]