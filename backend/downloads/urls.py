from django.urls import path

from .views import (
    DownloadRequestAPIView,
    PermanentDownloadListAPIView,
    MovieStreamAPIView,
    PermanentDownloadAccessAPIView,
)


urlpatterns = [

    path(
        "",
        PermanentDownloadListAPIView.as_view(),
        name="permanent-download-list",
    ),

    path(
        "movies/<int:movie_id>/",
        DownloadRequestAPIView.as_view(),
        name="download-request",
    ),

    path(
        "movies/<int:movie_id>/stream/",
        MovieStreamAPIView.as_view(),
        name="movie-stream",
    ),

    path(
        "movies/<int:movie_id>/offline/",
        PermanentDownloadAccessAPIView.as_view(),
        name="movie-offline-access",
    ),
]