"""
MovieTime download API views.

Chapter 78 — Abuse Prevention

Download endpoints are protected by:

    - authentication;
    - rate limiting;
    - backend authorization;
    - object-level ownership checks;
    - duplicate download prevention.

Download authorization requires:

    Active Subscription
            OR
    Paid Permanent Purchase

PermanentDownload represents download state.

It does NOT represent movie ownership.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.abuse_prevention import (
    AbusePreventionService,
    InvalidOperationError,
)
from config.throttling import DownloadRateThrottle

from .services import (
    DownloadAuthorizationError,
    DownloadNotFoundError,
    DownloadService,
    DownloadStateError,
)


def download_to_dict(download):
    """
    Convert a PermanentDownload object into an API-safe response.
    """

    return {
        "id": download.id,
        "movie_id": download.movie_id,
        "status": download.status,
        "created_at": download.created_at,
        "downloaded_at": download.downloaded_at,
        "updated_at": download.updated_at,
    }


# ====================================================================
# DOWNLOAD MOVIE
# ====================================================================

class DownloadMovieAPIView(APIView):
    """
    Create or retrieve a user's download record.

    POST /api/v1/downloads/movies/<movie_id>/
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [DownloadRateThrottle]

    def post(self, request, movie_id):

        try:
            movie_id = AbusePreventionService.normalize_identifier(
                movie_id
            )

            movie_id = int(movie_id)

        except (InvalidOperationError, ValueError) as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie = DownloadService.get_movie(movie_id)

            download = DownloadService.create_download(
                user=request.user,
                movie=movie,
            )

        except DownloadAuthorizationError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            download_to_dict(download),
            status=status.HTTP_200_OK,
        )


# ====================================================================
# DOWNLOAD LIST
# ====================================================================

class DownloadListAPIView(APIView):
    """
    Return the authenticated user's download library.

    GET /api/v1/downloads/
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [DownloadRateThrottle]

    def get(self, request):

        downloads = DownloadService.get_user_downloads(
            user=request.user,
        )

        results = [
            download_to_dict(download)
            for download in downloads
        ]

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


# ====================================================================
# STREAM DOWNLOADED MOVIE
# ====================================================================

class DownloadStreamAPIView(APIView):
    """
    Check whether a completed download exists.

    GET /api/v1/downloads/movies/<movie_id>/stream/

    Secure media URL generation is intentionally not implemented here.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [DownloadRateThrottle]

    def get(self, request, movie_id):

        try:
            movie_id = int(
                AbusePreventionService.normalize_identifier(movie_id)
            )

        except (InvalidOperationError, ValueError) as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie = DownloadService.get_movie(movie_id)

        except DownloadAuthorizationError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        completed = DownloadService.has_completed_download(
            user=request.user,
            movie=movie,
        )

        if not completed:
            return Response(
                {
                    "movie_id": movie.id,
                    "available": False,
                    "stream_url": None,
                    "detail": "Completed download not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "movie_id": movie.id,
                "available": True,
                "stream_url": None,
                "detail": (
                    "Completed download exists. "
                    "Secure media delivery will be provided "
                    "by the media-access layer."
                ),
            },
            status=status.HTTP_200_OK,
        )


# ====================================================================
# OFFLINE ACCESS
# ====================================================================

class DownloadOfflineAccessAPIView(APIView):
    """
    Check whether the user has a completed offline download.

    GET /api/v1/downloads/movies/<movie_id>/offline/
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [DownloadRateThrottle]

    def get(self, request, movie_id):

        try:
            movie_id = int(
                AbusePreventionService.normalize_identifier(movie_id)
            )

        except (InvalidOperationError, ValueError) as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie = DownloadService.get_movie(movie_id)

        except DownloadAuthorizationError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        completed = DownloadService.has_completed_download(
            user=request.user,
            movie=movie,
        )

        return Response(
            {
                "movie_id": movie.id,
                "offline_available": completed,
            },
            status=status.HTTP_200_OK,
        )


# ====================================================================
# DOWNLOAD STATUS
# ====================================================================

class DownloadStatusAPIView(APIView):
    """
    Retrieve a user's download status.

    GET /api/v1/downloads/<download_id>/
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [DownloadRateThrottle]

    def get(self, request, download_id):

        try:
            download_id = int(
                AbusePreventionService.normalize_identifier(
                    download_id
                )
            )

        except (InvalidOperationError, ValueError) as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            download = DownloadService.get_download_or_raise(
                user=request.user,
                download_id=download_id,
            )

        except DownloadNotFoundError:
            return Response(
                {
                    "detail": "Download not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            download_to_dict(download),
            status=status.HTTP_200_OK,
        )


# ====================================================================
# START DOWNLOAD
# ====================================================================

class StartDownloadAPIView(APIView):
    """
    Move a download from PENDING to DOWNLOADING.

    POST /api/v1/downloads/<download_id>/start/
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [DownloadRateThrottle]

    def post(self, request, download_id):

        try:
            download_id = int(
                AbusePreventionService.normalize_identifier(
                    download_id
                )
            )

            download = DownloadService.mark_downloading(
                user=request.user,
                download_id=download_id,
            )

        except (InvalidOperationError, ValueError) as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except DownloadNotFoundError:
            return Response(
                {
                    "detail": "Download not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except DownloadStateError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            download_to_dict(download),
            status=status.HTTP_200_OK,
        )


# ====================================================================
# COMPLETE DOWNLOAD
# ====================================================================

class CompleteDownloadAPIView(APIView):
    """
    Mark a download as completed.

    POST /api/v1/downloads/<download_id>/complete/
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [DownloadRateThrottle]

    def post(self, request, download_id):

        try:
            download_id = int(
                AbusePreventionService.normalize_identifier(
                    download_id
                )
            )

            download = DownloadService.mark_completed(
                user=request.user,
                download_id=download_id,
            )

        except (InvalidOperationError, ValueError) as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except DownloadNotFoundError:
            return Response(
                {
                    "detail": "Download not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except DownloadStateError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            download_to_dict(download),
            status=status.HTTP_200_OK,
        )


# ====================================================================
# FAIL DOWNLOAD
# ====================================================================

class FailDownloadAPIView(APIView):
    """
    Mark a download as failed.

    POST /api/v1/downloads/<download_id>/failed/
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [DownloadRateThrottle]

    def post(self, request, download_id):

        try:
            download_id = int(
                AbusePreventionService.normalize_identifier(
                    download_id
                )
            )

            download = DownloadService.mark_failed(
                user=request.user,
                download_id=download_id,
            )

        except (InvalidOperationError, ValueError) as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except DownloadNotFoundError:
            return Response(
                {
                    "detail": "Download not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except DownloadStateError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            download_to_dict(download),
            status=status.HTTP_200_OK,
        )