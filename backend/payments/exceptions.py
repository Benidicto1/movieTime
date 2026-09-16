# backend/payments/exceptions.py


class PaymentError(Exception):
    """
    Base exception for MovieTime payment-related errors.
    """

    default_message = "A payment error occurred."

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class PaymentNotFoundError(PaymentError):
    """
    Raised when a requested payment cannot be found.
    """

    default_message = "Payment was not found."


class PaymentStateError(PaymentError):
    """
    Raised when an operation is not allowed for the current
    payment state.

    Example:
        Trying to initiate a payment that is already successful.
    """

    default_message = "The payment is in an invalid state for this operation."


class PaymentVerificationError(PaymentError):
    """
    Raised when payment verification fails.

    This can happen when:
        - provider reference is invalid
        - amount does not match
        - currency does not match
        - provider response cannot be trusted
        - callback authentication fails
        - payment belongs to another transaction
    """

    default_message = "Payment verification failed."


class PaymentProviderError(PaymentError):
    """
    Raised when communication with MTN or Airtel fails.
    """

    default_message = "The payment provider could not process the request."


class PaymentConfigurationError(PaymentError):
    """
    Raised when a payment provider has not been configured correctly.

    Examples:
        - Missing MTN API credentials
        - Missing Airtel API credentials
        - Missing callback configuration
        - Missing provider base URL
    """

    default_message = "Payment provider configuration is incomplete."


class PaymentAmountMismatchError(PaymentVerificationError):
    """
    Raised when the amount returned by the payment provider
    does not match the amount stored by MovieTime.
    """

    default_message = "Payment amount does not match the expected amount."


class PaymentCurrencyMismatchError(PaymentVerificationError):
    """
    Raised when the provider currency does not match the
    currency stored by MovieTime.
    """

    default_message = "Payment currency does not match the expected currency."


class PaymentReferenceError(PaymentVerificationError):
    """
    Raised when a provider reference is missing, invalid,
    duplicated, or does not belong to the expected payment.
    """

    default_message = "Payment provider reference is invalid."


class PaymentCallbackError(PaymentVerificationError):
    """
    Raised when a payment-provider callback cannot be trusted.

    Examples:
        - Invalid callback signature
        - Missing callback signature
        - Unknown provider
        - Invalid callback payload
    """

    default_message = "Payment callback verification failed."


class PaymentAlreadyCompletedError(PaymentStateError):
    """
    Raised when attempting to complete a payment that has
    already reached a terminal successful state.
    """

    default_message = "Payment has already been completed."


class PaymentAlreadyFailedError(PaymentStateError):
    """
    Raised when attempting to process a payment that has
    already failed.
    """

    default_message = "Payment has already failed."


class PaymentCancelledError(PaymentStateError):
    """
    Raised when attempting to process a cancelled payment.
    """

    default_message = "Payment has been cancelled."