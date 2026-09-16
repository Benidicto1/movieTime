# backend/payments/tests/test_security.py

from django.test import SimpleTestCase, override_settings

from payments.security import (
    generate_callback_signature,
    get_callback_secret,
    verify_callback_signature,
    verify_provider_callback,
)


class CallbackSignatureTests(SimpleTestCase):
    """
    Tests for payment-provider callback signature generation
    and verification.
    """

    def setUp(self):
        self.secret = "test-callback-secret"
        self.payload = (
            b'{"payment_id":123,"status":"SUCCESS","amount":"10000.00"}'
        )

    def test_generate_callback_signature_returns_hex_digest(self):
        signature = generate_callback_signature(
            payload=self.payload,
            secret=self.secret,
        )

        self.assertIsInstance(signature, str)
        self.assertEqual(len(signature), 64)

    def test_same_payload_and_secret_generate_same_signature(self):
        signature_one = generate_callback_signature(
            payload=self.payload,
            secret=self.secret,
        )

        signature_two = generate_callback_signature(
            payload=self.payload,
            secret=self.secret,
        )

        self.assertEqual(signature_one, signature_two)

    def test_different_secret_generates_different_signature(self):
        signature_one = generate_callback_signature(
            payload=self.payload,
            secret=self.secret,
        )

        signature_two = generate_callback_signature(
            payload=self.payload,
            secret="different-secret",
        )

        self.assertNotEqual(signature_one, signature_two)

    def test_different_payload_generates_different_signature(self):
        signature_one = generate_callback_signature(
            payload=self.payload,
            secret=self.secret,
        )

        signature_two = generate_callback_signature(
            payload=b'{"payment_id":999,"status":"SUCCESS"}',
            secret=self.secret,
        )

        self.assertNotEqual(signature_one, signature_two)

    def test_verify_valid_signature_returns_true(self):
        signature = generate_callback_signature(
            payload=self.payload,
            secret=self.secret,
        )

        result = verify_callback_signature(
            payload=self.payload,
            signature=signature,
            secret=self.secret,
        )

        self.assertTrue(result)

    def test_verify_invalid_signature_returns_false(self):
        result = verify_callback_signature(
            payload=self.payload,
            signature="invalid-signature",
            secret=self.secret,
        )

        self.assertFalse(result)

    def test_verify_modified_payload_returns_false(self):
        signature = generate_callback_signature(
            payload=self.payload,
            secret=self.secret,
        )

        modified_payload = (
            b'{"payment_id":123,"status":"FAILED","amount":"10000.00"}'
        )

        result = verify_callback_signature(
            payload=modified_payload,
            signature=signature,
            secret=self.secret,
        )

        self.assertFalse(result)

    def test_verify_wrong_secret_returns_false(self):
        signature = generate_callback_signature(
            payload=self.payload,
            secret=self.secret,
        )

        result = verify_callback_signature(
            payload=self.payload,
            signature=signature,
            secret="wrong-secret",
        )

        self.assertFalse(result)

    def test_signature_with_whitespace_is_accepted(self):
        signature = generate_callback_signature(
            payload=self.payload,
            secret=self.secret,
        )

        result = verify_callback_signature(
            payload=self.payload,
            signature=f"  {signature}  ",
            secret=self.secret,
        )

        self.assertTrue(result)

    def test_empty_signature_returns_false(self):
        result = verify_callback_signature(
            payload=self.payload,
            signature="",
            secret=self.secret,
        )

        self.assertFalse(result)

    def test_empty_secret_returns_false(self):
        result = verify_callback_signature(
            payload=self.payload,
            signature="some-signature",
            secret="",
        )

        self.assertFalse(result)

    def test_empty_payload_returns_false(self):
        result = verify_callback_signature(
            payload=b"",
            signature="some-signature",
            secret=self.secret,
        )

        self.assertFalse(result)

    def test_generate_signature_without_secret_raises_error(self):
        with self.assertRaises(ValueError):
            generate_callback_signature(
                payload=self.payload,
                secret="",
            )


@override_settings(
    MTN_CALLBACK_SECRET="mtn-test-secret",
    AIRTEL_CALLBACK_SECRET="airtel-test-secret",
)
class CallbackSecretTests(SimpleTestCase):
    """
    Tests provider-specific callback-secret retrieval.
    """

    def test_get_mtn_callback_secret(self):
        secret = get_callback_secret("MTN")

        self.assertEqual(
            secret,
            "mtn-test-secret",
        )

    def test_get_airtel_callback_secret(self):
        secret = get_callback_secret("AIRTEL")

        self.assertEqual(
            secret,
            "airtel-test-secret",
        )

    def test_provider_name_is_case_insensitive(self):
        mtn_secret = get_callback_secret("mtn")
        airtel_secret = get_callback_secret("airtel")

        self.assertEqual(
            mtn_secret,
            "mtn-test-secret",
        )

        self.assertEqual(
            airtel_secret,
            "airtel-test-secret",
        )

    def test_provider_name_whitespace_is_ignored(self):
        secret = get_callback_secret("  MTN  ")

        self.assertEqual(
            secret,
            "mtn-test-secret",
        )

    def test_unknown_provider_returns_none(self):
        secret = get_callback_secret("UNKNOWN")

        self.assertIsNone(secret)

    def test_empty_provider_returns_none(self):
        secret = get_callback_secret("")

        self.assertIsNone(secret)

    def test_none_provider_returns_none(self):
        secret = get_callback_secret(None)

        self.assertIsNone(secret)


@override_settings(
    MTN_CALLBACK_SECRET="mtn-test-secret",
    AIRTEL_CALLBACK_SECRET="airtel-test-secret",
)
class ProviderCallbackVerificationTests(SimpleTestCase):
    """
    Tests the high-level provider callback verification helper.
    """

    def setUp(self):
        self.payload = (
            b'{"payment_id":123,"status":"SUCCESS","amount":"10000.00"}'
        )

    def test_valid_mtn_callback_is_accepted(self):
        signature = generate_callback_signature(
            payload=self.payload,
            secret="mtn-test-secret",
        )

        result = verify_provider_callback(
            provider="MTN",
            payload=self.payload,
            signature=signature,
        )

        self.assertTrue(result)

    def test_valid_airtel_callback_is_accepted(self):
        signature = generate_callback_signature(
            payload=self.payload,
            secret="airtel-test-secret",
        )

        result = verify_provider_callback(
            provider="AIRTEL",
            payload=self.payload,
            signature=signature,
        )

        self.assertTrue(result)

    def test_mtn_signature_cannot_be_used_for_airtel(self):
        signature = generate_callback_signature(
            payload=self.payload,
            secret="mtn-test-secret",
        )

        result = verify_provider_callback(
            provider="AIRTEL",
            payload=self.payload,
            signature=signature,
        )

        self.assertFalse(result)

    def test_airtel_signature_cannot_be_used_for_mtn(self):
        signature = generate_callback_signature(
            payload=self.payload,
            secret="airtel-test-secret",
        )

        result = verify_provider_callback(
            provider="MTN",
            payload=self.payload,
            signature=signature,
        )

        self.assertFalse(result)

    def test_invalid_provider_is_rejected(self):
        result = verify_provider_callback(
            provider="UNKNOWN",
            payload=self.payload,
            signature="anything",
        )

        self.assertFalse(result)

    def test_modified_callback_is_rejected(self):
        signature = generate_callback_signature(
            payload=self.payload,
            secret="mtn-test-secret",
        )

        modified_payload = (
            b'{"payment_id":123,"status":"SUCCESS","amount":"999999.00"}'
        )

        result = verify_provider_callback(
            provider="MTN",
            payload=modified_payload,
            signature=signature,
        )

        self.assertFalse(result)

    def test_invalid_signature_is_rejected(self):
        result = verify_provider_callback(
            provider="MTN",
            payload=self.payload,
            signature="invalid-signature",
        )

        self.assertFalse(result)