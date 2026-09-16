"""
MovieTime movie URL configuration.

Chapter 78 — Abuse Prevention

Protected movie flow:

    /api/v1/movies/
        |
        +-- catalog
        |
        +-- movie details
        |
        +-- access check
        |
        +-- protected stream authorization
        |
        +-- download authorization

Authentication is handled by DRF permissions.

Authorization is handled by MovieAccessService.
"""

from django.urls import path

from .views import (
    MovieAccessAPIView,
    MovieDetailAPIView,
    MovieDownloadAccessAPIView,
    MovieListAPIView,
    MovieStreamAPIView,
)


app_name = "movies"


urlpatterns = [
    # ---------------------------------------------------------
    # Movie catalog
    # ---------------------------------------------------------

    path(
        "",
        MovieListAPIView.as_view(),
        name="movie-list",
    ),

    # ---------------------------------------------------------
    # Movie details
    # ---------------------------------------------------------

    path(
        "<int:pk>/",
        MovieDetailAPIView.as_view(),
        name="movie-detail",
    ),

    # ---------------------------------------------------------
    # Movie access status
    # ---------------------------------------------------------

    path(
        "<int:movie_id>/access/",
        MovieAccessAPIView.as_view(),
        name="movie-access",
    ),

    # ---------------------------------------------------------
    # Protected movie streaming
    # ---------------------------------------------------------

    path(
        "<int:movie_id>/stream/",
        MovieStreamAPIView.as_view(),
        name="movie-stream",
    ),

    # ---------------------------------------------------------
    # Download authorization
    # ---------------------------------------------------------

    path(
        "<int:movie_id>/download-access/",
        MovieDownloadAccessAPIView.as_view(),
        name="movie-download-access",
    ),
]