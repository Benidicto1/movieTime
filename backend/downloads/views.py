from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from movies.models import Movie

from .models import PermanentDownload
from .serializers import PermanentDownloadSerializer
from .services import (
    DownloadAuthorizationService,
    MediaAuthorizationService,
)


class DownloadRequestAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(
        self,
        request,
        movie_id,
    ):

        movie = get_object_or_404(
            Movie,
            id=movie_id,
            is_active=True,
        )

        try:

            download, created = (
                DownloadAuthorizationService
                .create_download(
                    user=request.user,
                    movie=movie,
                )
            )

        except PermissionError as error:

            return Response(
                {
                    "detail": str(error),
                },
                status=403,
            )

        serializer = (
            PermanentDownloadSerializer(
                download
            )
        )

        return Response(
            {
                "created": created,
                "download": serializer.data,
            },
            status=201 if created else 200,
        )


class PermanentDownloadListAPIView(
    generics.ListAPIView
):

    serializer_class = (
        PermanentDownloadSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        return (
            PermanentDownload.objects
            .filter(
                user=self.request.user,
                status=(
                    PermanentDownload
                    .Status
                    .COMPLETED
                ),
            )
            .select_related("movie")
        )


class MovieStreamAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        movie_id,
    ):

        movie = get_object_or_404(
            Movie,
            id=movie_id,
            is_active=True,
        )

        if not (
            MediaAuthorizationService
            .can_stream(
                user=request.user,
                movie=movie,
            )
        ):

            return Response(
                {
                    "detail": (
                        "An active subscription "
                        "is required to stream "
                        "this movie."
                    )
                },
                status=403,
            )

        return Response(
            {
                "movie": movie.id,
                "title": movie.title,
                "authorized": True,
                "streaming": True,
            },
            status=200,
        )


class PermanentDownloadAccessAPIView(
    APIView
):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        movie_id,
    ):

        movie = get_object_or_404(
            Movie,
            id=movie_id,
            is_active=True,
        )

        if not (
            MediaAuthorizationService
            .can_access_offline(
                user=request.user,
                movie=movie,
            )
        ):

            return Response(
                {
                    "detail": (
                        "You do not own "
                        "this movie."
                    )
                },
                status=403,
            )

        return Response(
            {
                "movie": movie.id,
                "title": movie.title,
                "owned": True,
                "offline_access": True,
            },
            status=200,
        )