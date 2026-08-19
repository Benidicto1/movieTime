from rest_framework import serializers

from .models import Favorite, Watchlist


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = [
            "id",
            "movie",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = [
            "id",
            "movie",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]