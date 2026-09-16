# backend/downloads/tests.py

"""
MovieTime download authorization tests.

Chapter 75
"""


from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from downloads.models import PermanentDownload
from downloads.services import (
    DownloadAuthorizationError,
    DownloadService,
)
from movies.models import Movie
from purchases.models import Purchase
from subscriptions.models import SubscriptionPlan


User = get_user_model()


class DownloadAuthorizationTests(TestCase):
    """
    Tests for backend-authoritative download authorization.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="downloadtest",
            password="StrongPassword123!",
        )

        self.movie = Movie.objects.create(
            title="Test Movie",
            description="Download authorization test movie.",
            price=Decimal("10000.00"),
            is_active=True,
        )

    def test_unpaid_user_cannot_download(self):
        """
        A user without a paid purchase or active subscription
        must not be able to create a download.
        """

        with self.assertRaises(DownloadAuthorizationError):
            DownloadService.create_download(
                user=self.user,
                movie=self.movie,
            )

        self.assertFalse(
            PermanentDownload.objects.filter(
                user=self.user,
                movie=self.movie,
            ).exists()
        )

    def test_paid_purchase_allows_download(self):
        """
        A PAID permanent purchase grants download authorization.
        """

        Purchase.objects.create(
            user=self.user,
            movie=self.movie,
            amount=self.movie.price,
            currency="UGX",
            status=Purchase.Status.PAID,
        )

        download = DownloadService.create_download(
            user=self.user,
            movie=self.movie,
        )

        self.assertEqual(
            download.user,
            self.user,
        )

        self.assertEqual(
            download.movie,
            self.movie,
        )

        self.assertEqual(
            download.status,
            PermanentDownload.Status.PENDING,
        )

    def test_pending_purchase_does_not_allow_download(self):
        """
        A pending payment/purchase does not grant access.
        """

        Purchase.objects.create(
            user=self.user,
            movie=self.movie,
            amount=self.movie.price,
            currency="UGX",
            status=Purchase.Status.PENDING,
        )

        with self.assertRaises(DownloadAuthorizationError):
            DownloadService.create_download(
                user=self.user,
                movie=self.movie,
            )

    def test_failed_purchase_does_not_allow_download(self):
        """
        A failed purchase does not grant access.
        """

        Purchase.objects.create(
            user=self.user,
            movie=self.movie,
            amount=self.movie.price,
            currency="UGX",
            status=Purchase.Status.FAILED,
        )

        with self.assertRaises(DownloadAuthorizationError):
            DownloadService.create_download(
                user=self.user,
                movie=self.movie,
            )

    def test_cancelled_purchase_does_not_allow_download(self):
        """
        A cancelled purchase does not grant access.
        """

        Purchase.objects.create(
            user=self.user,
            movie=self.movie,
            amount=self.movie.price,
            currency="UGX",
            status=Purchase.Status.CANCELLED,
        )

        with self.assertRaises(DownloadAuthorizationError):
            DownloadService.create_download(
                user=self.user,
                movie=self.movie,
            )

    def test_existing_download_is_not_duplicate(self):
        """
        Creating the same authorized download twice should return
        the existing record.
        """

        Purchase.objects.create(
            user=self.user,
            movie=self.movie,
            amount=self.movie.price,
            currency="UGX",
            status=Purchase.Status.PAID,
        )

        first_download = DownloadService.create_download(
            user=self.user,
            movie=self.movie,
        )

        second_download = DownloadService.create_download(
            user=self.user,
            movie=self.movie,
        )

        self.assertEqual(
            first_download.id,
            second_download.id,
        )

        self.assertEqual(
            PermanentDownload.objects.filter(
                user=self.user,
                movie=self.movie,
            ).count(),
            1,
        )

    def test_completed_download_is_not_ownership_source(self):
        """
        A completed download record alone must not grant authorization.

        This protects against treating a stale/local download record
        as proof of purchase.
        """

        download = PermanentDownload.objects.create(
            user=self.user,
            movie=self.movie,
            status=PermanentDownload.Status.COMPLETED,
        )

        self.assertFalse(
            DownloadService.can_download(
                user=self.user,
                movie=self.movie,
            )
        )

        self.assertEqual(
            download.status,
            PermanentDownload.Status.COMPLETED,
        )