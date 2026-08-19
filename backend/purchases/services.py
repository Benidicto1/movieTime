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
        existing_purchase = Purchase.objects.filter(
            user=user,
            movie=movie,
            status=Purchase.Status.PAID,
        ).first()

        if existing_purchase:
            raise ValueError(
                "User already owns this movie."
            )

        purchase = Purchase.objects.create(
            user=user,
            movie=movie,
            amount=movie.price,
            currency="UGX",
            status=Purchase.Status.PENDING,
        )

        return purchase


    class PurchaseService:

        @staticmethod
        def user_owns_movie(
            *,
            user,
            movie,
        ):
            return Purchase.objects.filter(
                user=user,
                movie=movie,
                status=Purchase.Status.PAID,
            ).exists()