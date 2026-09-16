"""
Tests for MovieTime abuse prevention.

Chapter 78 — Abuse Prevention
"""

from decimal import Decimal

from django.test import SimpleTestCase

from config.abuse_prevention import (
    AbusePreventionError,
    AbusePreventionService,
    DuplicateOperationError,
    InvalidOperationError,
    PaymentReplayError,
)


class AbusePreventionTests(SimpleTestCase):
    """
    Unit tests for MovieTime abuse-prevention utilities.
    """

    def test_positive_amount_is_accepted(self):
        amount = (
            AbusePreventionService.require_positive_amount(
                "4500"
            )
        )

        self.assertEqual(
            amount,
            Decimal("4500"),
        )

    def test_zero_amount_is_rejected(self):
        with self.assertRaises(InvalidOperationError):
            AbusePreventionService.require_positive_amount(
                "0"
            )

    def test_negative_amount_is_rejected(self):
        with self.assertRaises(InvalidOperationError):
            AbusePreventionService.require_positive_amount(
                "-100"
            )

    def test_invalid_amount_is_rejected(self):
        with self.assertRaises(InvalidOperationError):
            AbusePreventionService.require_positive_amount(
                "invalid"
            )

    def test_currency_is_normalized(self):
        currency = (
            AbusePreventionService.require_valid_currency(
                "ugx"
            )
        )

        self.assertEqual(
            currency,
            "UGX",
        )

    def test_invalid_currency_is_rejected(self):
        with self.assertRaises(InvalidOperationError):
            AbusePreventionService.require_valid_currency(
                "UG"
            )

    def test_provider_reference_is_required(self):
        with self.assertRaises(PaymentReplayError):
            AbusePreventionService.require_provider_reference(
                ""
            )

    def test_provider_reference_is_normalized(self):
        reference = (
            AbusePreventionService.require_provider_reference(
                "  ABC123  "
            )
        )

        self.assertEqual(
            reference,
            "ABC123",
        )

    def test_duplicate_operation_is_rejected(self):
        with self.assertRaises(DuplicateOperationError):
            AbusePreventionService.ensure_not_duplicate(
                object()
            )

    def test_new_operation_is_allowed(self):
        result = (
            AbusePreventionService.ensure_not_duplicate(
                None
            )
        )

        self.assertIsNone(result)

    def test_valid_state_is_accepted(self):
        result = (
            AbusePreventionService.ensure_state(
                "PENDING",
                {
                    "PENDING",
                    "PROCESSING",
                },
            )
        )

        self.assertTrue(result)

    def test_invalid_state_is_rejected(self):
        with self.assertRaises(InvalidOperationError):
            AbusePreventionService.ensure_state(
                "PAID",
                {
                    "PENDING",
                    "PROCESSING",
                },
            )

    def test_identifier_is_normalized(self):
        identifier = (
            AbusePreventionService.normalize_identifier(
                " 123 "
            )
        )

        self.assertEqual(
            identifier,
            "123",
        )

    def test_empty_identifier_is_rejected(self):
        with self.assertRaises(InvalidOperationError):
            AbusePreventionService.normalize_identifier(
                ""
            )

    def test_abuse_errors_have_expected_base_class(self):
        self.assertTrue(
            issubclass(
                DuplicateOperationError,
                AbusePreventionError,
            )
        )

        self.assertTrue(
            issubclass(
                InvalidOperationError,
                AbusePreventionError,
            )
        )

        self.assertTrue(
            issubclass(
                PaymentReplayError,
                AbusePreventionError,
            )
        )