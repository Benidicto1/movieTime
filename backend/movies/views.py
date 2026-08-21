from rest_framework import generics
from .permissions import IsAdminOrReadOnly
from .serializers import MovieSerializer
from rest_framework.filters import OrderingFilter
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .filters import MovieFilter
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Movie
from .services import StreamingService








class MovieStreamAPIView(APIView):

    permission_classes = [
        IsAuthenticated
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

        if not StreamingService.can_stream(
            user=request.user,
            movie=movie,
        ):
            return Response(
                {
                    "detail": (
                        "An active subscription "
                        "or permanent ownership "
                        "is required."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {
                "movie_id": movie.id,
                "message": "Streaming authorized.",
            },
            status=status.HTTP_200_OK,
        )


class MovieListCreateAPIView(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]

    filterset_class = MovieFilter

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "title",
        "release_date",
        "rating",
    ]

    ordering = [
        "-release_date",
    ]

class MovieDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAdminOrReadOnly]