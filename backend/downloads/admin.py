from django.contrib import admin

from .models import PermanentDownload


@admin.register(PermanentDownload)
class PermanentDownloadAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "movie",
        "status",
        "created_at",
        "downloaded_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "created_at",
        "downloaded_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "movie__title",
    )

    readonly_fields = (
        "created_at",
        "downloaded_at",
        "updated_at",
    )