from django.db import transaction

from .models import Purchase


class PurchaseService:

    @staticmethod
    @transaction.atomic
    def create_pending_purchase(
        *,
        user,
        movie,
    ):
        existing_paid_purchase = (
            Purchase.objects
            .filter(
                user=user,
                movie=movie,
                status=Purchase.Status.PAID,
            )
            .first()
        )

        if existing_paid_purchase:
            raise ValueError(
                "User already owns this movie."
            )

        existing_pending_purchase = (
            Purchase.objects
            .filter(
                user=user,
                movie=movie,
                status=Purchase.Status.PENDING,
            )
            .order_by("-created_at")
            .first()
        )

        if existing_pending_purchase:
            return existing_pending_purchase

        purchase = Purchase.objects.create(
            user=user,
            movie=movie,
            amount=movie.price,
            currency="UGX",
            status=Purchase.Status.PENDING,
        )

        return purchase

    @staticmethod
    def user_owns_movie(
        *,
        user,
        movie,
    ):
        return (
            Purchase.objects
            .filter(
                user=user,
                movie=movie,
                status=Purchase.Status.PAID,
            )
            .exists()
        )