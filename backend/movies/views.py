"""
MovieTime movie API views.

Chapter 78 — Abuse Prevention

Movie endpoints provide:
- Movie listing
- Movie details
- Movie access status
- Streaming authorization
- Download authorization

Security rules:
- Authentication is required.
- Streaming authorization is rate-limited.
- Users must have either an active subscription or permanent
  ownership before receiving streaming authorization.
- MovieAccessService is the authoritative authorization service.
- Private storage URL generation is intentionally not implemented
  in this chapter.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.abuse_prevention import (
    AbusePreventionService,
    InvalidOperationError,
)
from config.throttling import StreamRateThrottle

from .models import Movie
from .services import MovieAccessService


# ============================================================
# HELPERS
# ============================================================


def movie_to_dict(movie):
    """
    Convert a Movie object into a JSON-safe response dictionary.

    The fields below match the current Movie API structure.
    """

    return {
        "id": movie.id,
        "title": movie.title,
        "description": movie.description,
        "release_date": movie.release_date,
        "duration": movie.duration,
        "age_rating": movie.age_rating,
        "genre_id": movie.genre_id,
    }


# ============================================================
# MOVIE LIST
# ============================================================


class MovieListAPIView(APIView):
    """
    Return a list of available movies.

    GET /api/v1/movies/
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        """
        Return movies.

        Optional query parameters:

            ?search=keyword
            ?genre=1
            ?ordering=created_at
        """

        movies = Movie.objects.filter(
            is_active=True,
        )

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        search = request.query_params.get("search")

        if search:
            search = search.strip()

            if len(search) > 100:
                return Response(
                    {
                        "detail": "Search query is too long.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            movies = movies.filter(
                title__icontains=search,
            )

        # ----------------------------------------------------
        # Genre filter
        # ----------------------------------------------------

        genre = request.query_params.get("genre")

        if genre:
            try:
                genre = (
                    AbusePreventionService
                    .normalize_identifier(genre)
                )

            except InvalidOperationError as exc:
                return Response(
                    {
                        "detail": str(exc),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            movies = movies.filter(
                genre_id=genre,
            )

        # ----------------------------------------------------
        # Ordering
        # ----------------------------------------------------

        ordering = request.query_params.get("ordering")

        allowed_ordering = {
            "title",
            "-title",
            "created_at",
            "-created_at",
            "release_date",
            "-release_date",
        }

        if ordering in allowed_ordering:
            movies = movies.order_by(ordering)
        else:
            movies = movies.order_by("-created_at")

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        results = [
            movie_to_dict(movie)
            for movie in movies
        ]

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# MOVIE DETAIL
# ============================================================


class MovieDetailAPIView(APIView):
    """
    Return details for a single movie.

    GET /api/v1/movies/<movie_id>/
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, pk):
        """
        Return movie details.
        """

        try:
            movie_id = (
                AbusePreventionService
                .normalize_identifier(pk)
            )

        except InvalidOperationError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie = Movie.objects.get(
                id=movie_id,
                is_active=True,
            )

        except Movie.DoesNotExist:
            return Response(
                {
                    "detail": "Movie not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            movie_to_dict(movie),
            status=status.HTTP_200_OK,
        )


# ============================================================
# MOVIE ACCESS
# ============================================================


class MovieAccessAPIView(APIView):
    """
    Return the current user's access status for a movie.

    GET /api/v1/movies/<movie_id>/access/

    Possible access types:

        purchase
        subscription
        none
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, movie_id):
        """
        Determine whether the authenticated user can access
        the requested movie.
        """

        try:
            movie_id = (
                AbusePreventionService
                .normalize_identifier(movie_id)
            )

        except InvalidOperationError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie = Movie.objects.get(
                id=movie_id,
            )

        except Movie.DoesNotExist:
            return Response(
                {
                    "detail": "Movie not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        result = MovieAccessService.get_access_result(
            user=request.user,
            movie=movie,
        )

        return Response(
            {
                "movie_id": movie.id,
                "access_granted": result.access_granted,
                "access_type": result.access_type,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# MOVIE STREAM
# ============================================================


class MovieStreamAPIView(APIView):
    """
    Authorize streaming of a movie.

    GET /api/v1/movies/<movie_id>/stream/

    A user must have either:

        1. An active subscription, OR
        2. Permanent ownership through a paid Purchase.

    IMPORTANT:

    The current MovieAccessService performs authorization but
    does not generate signed storage URLs.

    Therefore this endpoint does NOT expose a fake/public
    movie URL. Secure media delivery will be implemented
    separately.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    throttle_classes = [
        StreamRateThrottle,
    ]

    def get(self, request, movie_id):
        """
        Authorize the user's movie stream.
        """

        try:
            movie_id = (
                AbusePreventionService
                .normalize_identifier(movie_id)
            )

        except InvalidOperationError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie = Movie.objects.get(
                id=movie_id,
            )

        except Movie.DoesNotExist:
            return Response(
                {
                    "detail": "Movie not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------------------------------
        # Backend authorization
        # ----------------------------------------------------

        try:
            access_result = (
                MovieAccessService.authorize_stream(
                    user=request.user,
                    movie=movie,
                )
            )

        except Exception as exc:
            from django.core.exceptions import PermissionDenied

            if isinstance(exc, PermissionDenied):
                return Response(
                    {
                        "detail": str(exc),
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            raise

        # ----------------------------------------------------
        # Secure media delivery not implemented yet
        # ----------------------------------------------------

        return Response(
            {
                "movie_id": movie.id,
                "title": movie.title,
                "access_granted": True,
                "access_type": access_result.access_type,
                "stream_url": None,
                "message": (
                    "Streaming authorization succeeded. "
                    "Secure media URL generation will be "
                    "implemented in the media-delivery chapter."
                ),
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# MOVIE DOWNLOAD ACCESS
# ============================================================


class MovieDownloadAccessAPIView(APIView):
    """
    Authorize whether the user may download a movie.

    GET /api/v1/movies/<movie_id>/download-access/

    This endpoint only performs authorization.

    It does not create a download record and does not
    generate a download URL.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, movie_id):
        """
        Check download authorization.
        """

        try:
            movie_id = (
                AbusePreventionService
                .normalize_identifier(movie_id)
            )

        except InvalidOperationError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            movie = Movie.objects.get(
                id=movie_id,
            )

        except Movie.DoesNotExist:
            return Response(
                {
                    "detail": "Movie not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            access_result = (
                MovieAccessService.authorize_download(
                    user=request.user,
                    movie=movie,
                )
            )

        except Exception as exc:
            from django.core.exceptions import PermissionDenied

            if isinstance(exc, PermissionDenied):
                return Response(
                    {
                        "detail": str(exc),
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            raise

        return Response(
            {
                "movie_id": movie.id,
                "download_allowed": True,
                "access_type": access_result.access_type,
            },
            status=status.HTTP_200_OK,
        )