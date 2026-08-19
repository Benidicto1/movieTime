from django.contrib import admin

from .models import Favorite, Watchlist


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "movie",
        "created_at",
    ]

    search_fields = [
        "user__email",
        "movie__title",
    ]


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "movie",
        "created_at",
    ]

    search_fields = [
        "user__email",
        "movie__title",
    ]