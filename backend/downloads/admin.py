from django.contrib import admin

from .models import PermanentDownload


@admin.register(PermanentDownload)
class PermanentDownloadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "movie",
        "is_available",
    )

    list_filter = (
        "is_available",
    )

    search_fields = (
        "user__username",
        "user__email",
        "movie__title",
    )