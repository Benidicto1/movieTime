from rest_framework import generics
from .models import Movie
from .permissions import IsAdminOrReadOnly
from .serializers import MovieSerializer
from rest_framework.filters import OrderingFilter
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .filters import MovieFilter



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