from django.urls import path

from .views import (
    MovieListCreateAPIView,
    MovieDetailAPIView,
    MovieStreamAPIView,
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

    path(
        "<int:movie_id>/stream/",
        MovieStreamAPIView.as_view(),
        name="movie-stream",
    ),
]