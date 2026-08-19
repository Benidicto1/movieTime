from django.conf import settings
from django.db import models

from movies.models import Movie


class Download(models.Model):

    class Status(models.TextChoices):
        AUTHORIZED = "AUTHORIZED", "Authorized"
        STARTED = "STARTED", "Started"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="downloads",
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.PROTECT,
        related_name="downloads",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AUTHORIZED,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user} - {self.movie} - {self.status}"





class PermanentDownload(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="permanent_downloads",
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.PROTECT,
        related_name="permanent_downloads",
    )

    downloaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    is_available = models.BooleanField(
        default=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie"],
                name="unique_user_movie_download",
            )
        ]

    def __str__(self):
        return (
            f"{self.user} - "
            f"{self.movie.title}"
        )