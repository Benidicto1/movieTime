import django_filters

from .models import Movie


class MovieFilter(django_filters.FilterSet):

    release_year = django_filters.NumberFilter(
        field_name="release_date",
        lookup_expr="year",
    )

    rating_min = django_filters.NumberFilter(
        field_name="rating",
        lookup_expr="gte",
    )

    rating_max = django_filters.NumberFilter(
        field_name="rating",
        lookup_expr="lte",
    )

    genre = django_filters.CharFilter(
    field_name="genres__name",
    lookup_expr="iexact",
    )

    class Meta:
        model = Movie
        fields = [
            "release_year",
            "rating_min",
            "rating_max",
            "genre",
        ]