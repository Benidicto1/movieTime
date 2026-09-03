from django.conf import settings
from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):

        SUBSCRIPTION = (
            "SUBSCRIPTION",
            "Subscription",
        )

        PAYMENT = (
            "PAYMENT",
            "Payment",
        )

        DOWNLOAD = (
            "DOWNLOAD",
            "Download",
        )

        MOVIE = (
            "MOVIE",
            "Movie",
        )

        ACCOUNT = (
            "ACCOUNT",
            "Account",
        )

        SYSTEM = (
            "SYSTEM",
            "System",
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:

        ordering = [
            "-created_at",
        ]

    def __str__(self):

        return (
            f"{self.user} - "
            f"{self.title}"
        )