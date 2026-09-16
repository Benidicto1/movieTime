"""
MovieTime download URL configuration.

Chapter 78 — Abuse Prevention

All download-management endpoints require authentication.
"""

from django.urls import path

from .views import (
    CompleteDownloadAPIView,
    DownloadListAPIView,
    DownloadMovieAPIView,
    DownloadOfflineAccessAPIView,
    DownloadStatusAPIView,
    DownloadStreamAPIView,
    FailDownloadAPIView,
    StartDownloadAPIView,
)


app_name = "downloads"


urlpatterns = [

    # ================================================================
    # Download a movie
    # ================================================================

    path(
        "movies/<int:movie_id>/",
        DownloadMovieAPIView.as_view(),
        name="download-movie",
    ),

    # ================================================================
    # User download library
    # ================================================================

    path(
        "",
        DownloadListAPIView.as_view(),
        name="download-list",
    ),

    # ================================================================
    # Stream downloaded movie
    # ================================================================

    path(
        "movies/<int:movie_id>/stream/",
        DownloadStreamAPIView.as_view(),
        name="download-stream",
    ),

    # ================================================================
    # Offline access
    # ================================================================

    path(
        "movies/<int:movie_id>/offline/",
        DownloadOfflineAccessAPIView.as_view(),
        name="download-offline",
    ),

    # ================================================================
    # Individual download
    # ================================================================

    path(
        "<int:download_id>/",
        DownloadStatusAPIView.as_view(),
        name="download-status",
    ),

    # ================================================================
    # Download lifecycle
    # ================================================================

    path(
        "<int:download_id>/start/",
        StartDownloadAPIView.as_view(),
        name="download-start",
    ),

    path(
        "<int:download_id>/complete/",
        CompleteDownloadAPIView.as_view(),
        name="download-complete",
    ),

    path(
        "<int:download_id>/failed/",
        FailDownloadAPIView.as_view(),
        name="download-failed",
    ),
]