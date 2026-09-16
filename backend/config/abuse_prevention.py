from decimal import Decimal


class AbusePreventionError(Exception):
    """
    Base exception for MovieTime abuse-prevention failures.
    """


class DuplicateOperationError(AbusePreventionError):
    """
    Raised when an operation has already been performed.
    """


class InvalidOperationError(AbusePreventionError):
    """
    Raised when an operation is not valid for the current state.
    """


class PaymentReplayError(AbusePreventionError):
    """
    Raised when a provider reference has already been processed.
    """


class AbusePreventionService:
    """
    Centralized business-level abuse-prevention helpers.
    """

    @staticmethod
    def require_positive_amount(amount):
        """
        Ensure a payment amount is positive.
        """

        try:
            value = Decimal(str(amount))
        except (TypeError, ValueError):
            raise InvalidOperationError(
                "Invalid payment amount."
            )

        if value <= Decimal("0"):
            raise InvalidOperationError(
                "Payment amount must be greater than zero."
            )

        return value

    @staticmethod
    def require_valid_currency(currency):
        """
        Validate the payment currency.
        """

        if not currency:
            raise InvalidOperationError(
                "Payment currency is required."
            )

        currency = str(currency).upper().strip()

        if len(currency) != 3:
            raise InvalidOperationError(
                "Invalid payment currency."
            )

        return currency

    @staticmethod
    def require_provider_reference(provider_reference):
        """
        Validate a provider transaction reference.
        """

        if not provider_reference:
            raise PaymentReplayError(
                "Provider reference is required."
            )

        provider_reference = str(
            provider_reference
        ).strip()

        if not provider_reference:
            raise PaymentReplayError(
                "Provider reference cannot be empty."
            )

        return provider_reference

    @staticmethod
    def ensure_not_duplicate(existing_object):
        """
        Reject an operation when an existing object already
        represents the same operation.
        """

        if existing_object is not None:
            raise DuplicateOperationError(
                "This operation has already been processed."
            )

    @staticmethod
    def ensure_state(current_state, allowed_states):
        """
        Ensure that the current object state allows the
        requested operation.
        """

        if current_state not in allowed_states:
            raise InvalidOperationError(
                "This operation is not valid in the current state."
            )

        return True

    @staticmethod
    def normalize_identifier(identifier):
        """
        Normalize an externally supplied identifier.
        """

        if identifier is None:
            raise InvalidOperationError(
                "Identifier is required."
            )

        value = str(identifier).strip()

        if not value:
            raise InvalidOperationError(
                "Identifier cannot be empty."
            )

        return value