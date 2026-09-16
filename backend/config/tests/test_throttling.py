from django.contrib.auth import get_user_model
from django.test import override_settings

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, APITestCase

from config.throttling import (
    AuthenticationRateThrottle,
    DownloadRateThrottle,
    PaymentRateThrottle,
    PaymentStatusRateThrottle,
    PurchaseRateThrottle,
    StreamRateThrottle,
)


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_THROTTLE_RATES": {
            "anon": "30/minute",
            "user": "120/minute",
            "authentication": "5/minute",
            "payment": "10/minute",
            "purchase": "10/minute",
            "download": "20/minute",
            "stream": "30/minute",
            "payment_status": "30/minute",
        },
    }
)
class MovieTimeThrottleTests(APITestCase):
    """
    Test MovieTime-specific throttle classes.
    """

    def setUp(self):
        self.factory = APIRequestFactory()

        self.user_model = get_user_model()

        self.user = self.user_model.objects.create_user(
            username="throttleuser",
            email="throttle@example.com",
            password="StrongPassword123!",
        )

        self.other_user = self.user_model.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="StrongPassword123!",
        )

    def build_request(self, path="/api/v1/test/"):
        """
        Build a DRF Request object from an APIRequestFactory request.
        """

        django_request = self.factory.get(
            path,
            REMOTE_ADDR="127.0.0.1",
        )

        return Request(django_request)

    def build_authenticated_request(self, user):
        """
        Build an authenticated DRF Request.
        """

        django_request = self.factory.get(
            "/api/v1/test/",
            REMOTE_ADDR="127.0.0.1",
        )

        django_request.user = user

        return Request(django_request)

    def test_authentication_throttle_has_correct_scope(self):
        """
        AuthenticationRateThrottle should use the authentication scope.
        """

        throttle = AuthenticationRateThrottle()

        self.assertEqual(
            throttle.scope,
            "authentication",
        )

    def test_payment_throttle_has_correct_scope(self):
        """
        PaymentRateThrottle should use the payment scope.
        """

        throttle = PaymentRateThrottle()

        self.assertEqual(
            throttle.scope,
            "payment",
        )

    def test_purchase_throttle_has_correct_scope(self):
        """
        PurchaseRateThrottle should use the purchase scope.
        """

        throttle = PurchaseRateThrottle()

        self.assertEqual(
            throttle.scope,
            "purchase",
        )

    def test_download_throttle_has_correct_scope(self):
        """
        DownloadRateThrottle should use the download scope.
        """

        throttle = DownloadRateThrottle()

        self.assertEqual(
            throttle.scope,
            "download",
        )

    def test_stream_throttle_has_correct_scope(self):
        """
        StreamRateThrottle should use the stream scope.
        """

        throttle = StreamRateThrottle()

        self.assertEqual(
            throttle.scope,
            "stream",
        )

    def test_payment_status_throttle_has_correct_scope(self):
        """
        PaymentStatusRateThrottle should use the payment_status scope.
        """

        throttle = PaymentStatusRateThrottle()

        self.assertEqual(
            throttle.scope,
            "payment_status",
        )

    def test_authentication_throttle_uses_ip_address(self):
        """
        Authentication throttling should identify anonymous clients
        using their IP address.
        """

        request = self.build_request()

        throttle = AuthenticationRateThrottle()

        cache_key = throttle.get_cache_key(
            request,
            None,
        )

        self.assertIsNotNone(cache_key)

        self.assertIn(
            "127.0.0.1",
            cache_key,
        )

    def test_payment_throttle_uses_user_id_for_authenticated_user(self):
        """
        Payment throttling should identify authenticated users by
        their user ID rather than only by IP address.
        """

        request = self.build_authenticated_request(
            self.user,
        )

        throttle = PaymentRateThrottle()

        cache_key = throttle.get_cache_key(
            request,
            None,
        )

        self.assertIsNotNone(cache_key)

        self.assertIn(
            f"user:{self.user.pk}",
            cache_key,
        )

    def test_purchase_throttle_uses_user_id(self):
        """
        Purchase throttling should identify authenticated users
        by their user ID.
        """

        request = self.build_authenticated_request(
            self.user,
        )

        throttle = PurchaseRateThrottle()

        cache_key = throttle.get_cache_key(
            request,
            None,
        )

        self.assertIsNotNone(cache_key)

        self.assertIn(
            f"user:{self.user.pk}",
            cache_key,
        )

    def test_download_throttle_uses_user_id(self):
        """
        Download throttling should identify authenticated users
        by their user ID.
        """

        request = self.build_authenticated_request(
            self.user,
        )

        throttle = DownloadRateThrottle()

        cache_key = throttle.get_cache_key(
            request,
            None,
        )

        self.assertIsNotNone(cache_key)

        self.assertIn(
            f"user:{self.user.pk}",
            cache_key,
        )

    def test_stream_throttle_uses_user_id(self):
        """
        Stream throttling should identify authenticated users
        by their user ID.
        """

        request = self.build_authenticated_request(
            self.user,
        )

        throttle = StreamRateThrottle()

        cache_key = throttle.get_cache_key(
            request,
            None,
        )

        self.assertIsNotNone(cache_key)

        self.assertIn(
            f"user:{self.user.pk}",
            cache_key,
        )

    def test_payment_status_throttle_uses_user_id(self):
        """
        Payment-status throttling should identify authenticated users
        by their user ID.
        """

        request = self.build_authenticated_request(
            self.user,
        )

        throttle = PaymentStatusRateThrottle()

        cache_key = throttle.get_cache_key(
            request,
            None,
        )

        self.assertIsNotNone(cache_key)

        self.assertIn(
            f"user:{self.user.pk}",
            cache_key,
        )

    def test_purchase_throttle_does_not_throttle_anonymous_users(self):
        """
        PurchaseRateThrottle returns None for anonymous users.

        Anonymous traffic can still be protected by the global
        anonymous throttle configured in DRF.
        """

        request = self.build_request()

        throttle = PurchaseRateThrottle()

        cache_key = throttle.get_cache_key(
            request,
            None,
        )

        self.assertIsNone(cache_key)

    def test_download_throttle_does_not_throttle_anonymous_users(self):
        """
        DownloadRateThrottle returns None for anonymous users.
        """

        request = self.build_request()

        throttle = DownloadRateThrottle()

        cache_key = throttle.get_cache_key(
            request,
            None,
        )

        self.assertIsNone(cache_key)

    def test_stream_throttle_does_not_throttle_anonymous_users(self):
        """
        StreamRateThrottle returns None for anonymous users.
        """

        request = self.build_request()

        throttle = StreamRateThrottle()

        cache_key = throttle.get_cache_key(
            request,
            None,
        )

        self.assertIsNone(cache_key)

    def test_payment_status_throttle_does_not_throttle_anonymous_users(self):
        """
        PaymentStatusRateThrottle returns None for anonymous users.
        """

        request = self.build_request()

        throttle = PaymentStatusRateThrottle()

        cache_key = throttle.get_cache_key(
            request,
            None,
        )

        self.assertIsNone(cache_key)

    def test_different_users_receive_different_payment_keys(self):
        """
        Two authenticated users must receive different payment
        throttle cache keys.
        """

        request_one = self.build_authenticated_request(
            self.user,
        )

        request_two = self.build_authenticated_request(
            self.other_user,
        )

        throttle = PaymentRateThrottle()

        key_one = throttle.get_cache_key(
            request_one,
            None,
        )

        key_two = throttle.get_cache_key(
            request_two,
            None,
        )

        self.assertIsNotNone(key_one)
        self.assertIsNotNone(key_two)

        self.assertNotEqual(
            key_one,
            key_two,
        )

    def test_different_users_receive_different_purchase_keys(self):
        """
        Two authenticated users must receive different purchase
        throttle cache keys.
        """

        request_one = self.build_authenticated_request(
            self.user,
        )

        request_two = self.build_authenticated_request(
            self.other_user,
        )

        throttle = PurchaseRateThrottle()

        key_one = throttle.get_cache_key(
            request_one,
            None,
        )

        key_two = throttle.get_cache_key(
            request_two,
            None,
        )

        self.assertIsNotNone(key_one)
        self.assertIsNotNone(key_two)

        self.assertNotEqual(
            key_one,
            key_two,
        )

    def test_different_users_receive_different_download_keys(self):
        """
        Two authenticated users must receive different download
        throttle cache keys.
        """

        request_one = self.build_authenticated_request(
            self.user,
        )

        request_two = self.build_authenticated_request(
            self.other_user,
        )

        throttle = DownloadRateThrottle()

        key_one = throttle.get_cache_key(
            request_one,
            None,
        )

        key_two = throttle.get_cache_key(
            request_two,
            None,
        )

        self.assertIsNotNone(key_one)
        self.assertIsNotNone(key_two)

        self.assertNotEqual(
            key_one,
            key_two,
        )

    def test_different_users_receive_different_stream_keys(self):
        """
        Two authenticated users must receive different stream
        throttle cache keys.
        """

        request_one = self.build_authenticated_request(
            self.user,
        )

        request_two = self.build_authenticated_request(
            self.other_user,
        )

        throttle = StreamRateThrottle()

        key_one = throttle.get_cache_key(
            request_one,
            None,
        )

        key_two = throttle.get_cache_key(
            request_two,
            None,
        )

        self.assertIsNotNone(key_one)
        self.assertIsNotNone(key_two)

        self.assertNotEqual(
            key_one,
            key_two,
        )

    def test_different_users_receive_different_payment_status_keys(self):
        """
        Two authenticated users must receive different payment-status
        throttle cache keys.
        """

        request_one = self.build_authenticated_request(
            self.user,
        )

        request_two = self.build_authenticated_request(
            self.other_user,
        )

        throttle = PaymentStatusRateThrottle()

        key_one = throttle.get_cache_key(
            request_one,
            None,
        )

        key_two = throttle.get_cache_key(
            request_two,
            None,
        )

        self.assertIsNotNone(key_one)
        self.assertIsNotNone(key_two)

        self.assertNotEqual(
            key_one,
            key_two,
        )
