from django.contrib import admin
from django.urls import include, path


from .views import (
    FavoriteListCreateAPIView,
    FavoriteDetailAPIView,
    WatchlistListCreateAPIView,
    WatchlistDetailAPIView,
)


urlpatterns = [
    path(
        "favorites/",
        FavoriteListCreateAPIView.as_view(),
        name="favorite-list",
    ),

    path(
        "favorites/<int:pk>/",
        FavoriteDetailAPIView.as_view(),
        name="favorite-detail",
    ),

    path(
        "watchlist/",
        WatchlistListCreateAPIView.as_view(),
        name="watchlist-list",
    ),

    path(
        "watchlist/<int:pk>/",
        WatchlistDetailAPIView.as_view(),
        name="watchlist-detail",
    ),
]