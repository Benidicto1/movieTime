from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import MovieFilter
from .media_services import MediaDeliveryService
from .models import Movie
from .permissions import IsAdminOrReadOnly
from .serializers import MovieSerializer
from .services import MovieAccessService


class MovieListCreateAPIView(
    generics.ListCreateAPIView
):

    queryset = Movie.objects.all()

    serializer_class = MovieSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]

    filterset_class = MovieFilter

    ordering_fields = [
        "title",
        "release_date",
    ]

    ordering = [
        "-release_date",
    ]

    search_fields = [
        "title",
        "description",
    ]


class MovieDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Movie.objects.all()

    serializer_class = MovieSerializer

    permission_classes = [
        IsAdminOrReadOnly,
    ]


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

        if not MovieAccessService.can_stream(
            user=request.user,
            movie=movie,
        ):

            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to stream this movie."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        stream_url = (
            MediaDeliveryService.get_stream_url(
                movie=movie,
                user=request.user,
            )
        )

        return Response(
            {
                "movie_id": movie.id,
                "stream_url": stream_url,
            }
        )