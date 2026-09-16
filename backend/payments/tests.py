from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from movies.models import Movie
from purchases.models import Purchase
from subscriptions.models import (
    SubscriptionOrder,
    SubscriptionPlan,
)

from .models import Payment
from .services import (
    PaymentService,
    PaymentVerificationService,
)


User = get_user_model()


class PaymentServiceTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="paymentuser",
            password="StrongPassword123!",
        )

        self.movie = Movie.objects.create(
            title="Test Movie",
            slug="test-movie",
            description="Test movie.",
            price=Decimal("10000.00"),
            is_active=True,
        )

        self.plan = (
            SubscriptionPlan.objects.create(
                name="Test Day",
                plan_type=(
                    SubscriptionPlan
                    .PlanType
                    .DAY
                ),
                price=Decimal("900.00"),
                duration_days=1,
                is_active=True,
            )
        )

    def test_purchase_payment_uses_server_price(
        self,
    ):
        purchase = (
            Purchase.objects.create(
                user=self.user,
                movie=self.movie,
                amount=self.movie.price,
                currency="UGX",
                status=(
                    Purchase
                    .Status
                    .PENDING
                ),
            )
        )

        payment = (
            PaymentService.create_payment(
                purchase=purchase,
                provider="MTN",
            )
        )

        self.assertEqual(
            payment.amount,
            self.movie.price,
        )

        self.assertEqual(
            payment.currency,
            "UGX",
        )

        self.assertEqual(
            payment.purchase,
            purchase,
        )

        self.assertIsNone(
            payment.order
        )

    def test_payment_success_marks_purchase_paid(
        self,
    ):
        purchase = (
            Purchase.objects.create(
                user=self.user,
                movie=self.movie,
                amount=self.movie.price,
                currency="UGX",
                status=(
                    Purchase
                    .Status
                    .PENDING
                ),
            )
        )

        payment = (
            PaymentService.create_payment(
                purchase=purchase,
                provider="AIRTEL",
            )
        )

        PaymentVerificationService.mark_success(
            payment=payment,
            provider_reference="PROVIDER-123",
            verified_amount="10000.00",
            verified_currency="UGX",
        )

        purchase.refresh_from_db()

        payment.refresh_from_db()

        self.assertEqual(
            purchase.status,
            Purchase.Status.PAID,
        )

        self.assertIsNotNone(
            purchase.paid_at
        )

        self.assertEqual(
            payment.status,
            Payment.Status.SUCCESS,
        )

    def test_wrong_amount_is_rejected(
        self,
    ):
        purchase = (
            Purchase.objects.create(
                user=self.user,
                movie=self.movie,
                amount=self.movie.price,
                currency="UGX",
                status=(
                    Purchase
                    .Status
                    .PENDING
                ),
            )
        )

        payment = (
            PaymentService.create_payment(
                purchase=purchase,
                provider="MTN",
            )
        )

        with self.assertRaises(
            ValueError
        ):
            PaymentVerificationService.mark_success(
                payment=payment,
                provider_reference="PROVIDER-456",
                verified_amount="5000.00",
                verified_currency="UGX",
            )

    def test_wrong_currency_is_rejected(
        self,
    ):
        purchase = (
            Purchase.objects.create(
                user=self.user,
                movie=self.movie,
                amount=self.movie.price,
                currency="UGX",
                status=(
                    Purchase
                    .Status
                    .PENDING
                ),
            )
        )

        payment = (
            PaymentService.create_payment(
                purchase=purchase,
                provider="MTN",
            )
        )

        with self.assertRaises(
            ValueError
        ):
            PaymentVerificationService.mark_success(
                payment=payment,
                provider_reference="PROVIDER-789",
                verified_amount="10000.00",
                verified_currency="USD",
            )