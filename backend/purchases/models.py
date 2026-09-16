"""
MovieTime purchase model.

A Purchase represents ownership/payment state for a movie.

A PAID purchase grants permanent ownership.
"""

from django.conf import settings
from django.db import models

from movies.models import Movie


class Purchase(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"
        REFUNDED = "REFUNDED", "Refunded"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchases",
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.PROTECT,
        related_name="purchases",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default="UGX",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.user} - "
            f"{self.movie} - "
            f"{self.status}"
        )

    @property
    def is_owned(self):
        """
        A movie is permanently owned only after payment
        has been successfully verified.
        """

        return self.status == self.Status.PAID