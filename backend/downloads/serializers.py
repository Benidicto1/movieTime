from rest_framework import serializers

from .models import PermanentDownload


class PermanentDownloadSerializer(serializers.ModelSerializer):

    class Meta:
        model = PermanentDownload

        fields = [
            "id",
            "movie",
            "status",
            "created_at",
            "downloaded_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_at",
            "downloaded_at",
            "updated_at",
        ]