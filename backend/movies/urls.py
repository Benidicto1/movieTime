from django.urls import path

from .views import (
    MovieDetailAPIView,
    MovieListCreateAPIView,
)


urlpatterns = [
    path(
        "",
        MovieListCreateAPIView.as_view(),
        name="movie-list-create",
    ),

    path(
        "<int:pk>/",
        MovieDetailAPIView.as_view(),
        name="movie-detail",
    ),
]