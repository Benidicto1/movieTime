from django.conf import settings
from django.db import models

from movies.models import Movie






class PermanentDownload(models.Model):

    class Status(models.TextChoices):

        PENDING = (
            "pending",
            "Pending",
        )

        DOWNLOADING = (
            "downloading",
            "Downloading",
        )

        COMPLETED = (
            "completed",
            "Completed",
        )

        FAILED = (
            "failed",
            "Failed",
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="permanent_downloads",
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.PROTECT,
        related_name="permanent_downloads",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    downloaded_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "movie",
                ],
                name="unique_permanent_movie_owner",
            ),
        ]

        ordering = [
            "-created_at",
        ]

    def __str__(self):

        return (
            f"{self.user} - "
            f"{self.movie.title} - "
            f"{self.status}"
        )