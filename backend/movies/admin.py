
from django.contrib import admin
from .models import MovieMedia

from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "release_date",
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "slug",
    )

    list_filter = (
        "is_active",
        "release_date",
    )