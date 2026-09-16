from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from movies.models import Movie

from .models import Purchase
from .services import PurchaseService


User = get_user_model()


class PurchaseServiceTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="purchaseuser",
            password="StrongPassword123!",
        )

        self.movie = Movie.objects.create(
            title="Purchase Test Movie",
            slug="purchase-test-movie",
            description="Test movie.",
            price=Decimal("15000.00"),
            is_active=True,
        )

    def test_purchase_uses_movie_price(
        self,
    ):
        purchase = (
            PurchaseService
            .create_pending_purchase(
                user=self.user,
                movie=self.movie,
            )
        )

        self.assertEqual(
            purchase.amount,
            Decimal("15000.00"),
        )

        self.assertEqual(
            purchase.currency,
            "UGX",
        )

        self.assertEqual(
            purchase.status,
            Purchase.Status.PENDING,
        )

    def test_pending_purchase_is_reused(
        self,
    ):
        first = (
            PurchaseService
            .create_pending_purchase(
                user=self.user,
                movie=self.movie,
            )
        )

        second = (
            PurchaseService
            .create_pending_purchase(
                user=self.user,
                movie=self.movie,
            )
        )

        self.assertEqual(
            first.id,
            second.id,
        )

    def test_paid_purchase_means_ownership(
        self,
    ):
        Purchase.objects.create(
            user=self.user,
            movie=self.movie,
            amount=self.movie.price,
            currency="UGX",
            status=Purchase.Status.PAID,
        )

        self.assertTrue(
            PurchaseService.user_owns_movie(
                user=self.user,
                movie=self.movie,
            )
        )