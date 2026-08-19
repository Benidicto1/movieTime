from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from movies.models import Movie

from .models import Download
from .serializers import DownloadSerializer
from .services import DownloadAuthorizationService


class DownloadRequestAPIView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):

        movie_id = request.data.get("movie")

        movie = get_object_or_404(
            Movie,
            id=movie_id,
        )

        authorized = (
            DownloadAuthorizationService.can_download(
                user=request.user,
                movie=movie,
            )
        )

        if not authorized:
            return Response(
                {
                    "detail": (
                        "You must permanently own "
                        "this movie before downloading."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        download = Download.objects.create(
            user=request.user,
            movie=movie,
            status=Download.Status.AUTHORIZED,
        )

        serializer = DownloadSerializer(
            download
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )