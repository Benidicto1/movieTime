from django.contrib import admin

from .models import (
    Category,
    Country,
    Genre,
    Language,
    Movie,
    MovieCast,
    MovieCrew,
    MovieMedia,
    MovieVideo,
    Person,
    Subtitle,
)


@admin.register(MovieVideo)
class MovieVideoAdmin(admin.ModelAdmin):

    list_display = (
        "movie",
        "resolution",
        "status",
        "is_active",
        "created_at",
    )

    search_fields = (
        "movie__title",
        "storage_key",
    )

    list_filter = (
        "status",
        "is_active",
        "resolution",
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
    )

    list_filter = (
        "is_active",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "display_order",
        "is_active",
    )

    search_fields = (
        "name",
        "slug",
    )

    list_filter = (
        "is_active",
    )


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
    )

    search_fields = (
        "name",
        "code",
    )


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
    )

    search_fields = (
        "name",
        "code",
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "birth_date",
    )

    search_fields = (
        "name",
    )


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "release_date",
        "age_rating",
        "price",
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
    )

    list_filter = (
        "is_active",
        "age_rating",
        "release_date",
    )

    filter_horizontal = (
        "genres",
        "categories",
        "languages",
        "countries",
    )


@admin.register(MovieCast)
class MovieCastAdmin(admin.ModelAdmin):

    list_display = (
        "movie",
        "person",
        "character_name",
        "billing_order",
    )

    search_fields = (
        "movie__title",
        "person__name",
        "character_name",
    )


@admin.register(MovieCrew)
class MovieCrewAdmin(admin.ModelAdmin):

    list_display = (
        "movie",
        "person",
        "role",
    )

    search_fields = (
        "movie__title",
        "person__name",
        "role",
    )


@admin.register(MovieMedia)
class MovieMediaAdmin(admin.ModelAdmin):

    list_display = (
        "movie",
        "trailer_url",
        "movie_storage_key",
        "created_at",
    )

    search_fields = (
        "movie__title",
        "movie_storage_key",
    )


@admin.register(Subtitle)
class SubtitleAdmin(admin.ModelAdmin):

    list_display = (
        "movie",
        "language",
        "format",
        "is_active",
    )

    search_fields = (
        "movie__title",
        "language__name",
        "language__code",
    )

    list_filter = (
        "format",
        "is_active",
    )