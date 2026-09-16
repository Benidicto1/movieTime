# backend/payments/provider_result.py

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PaymentInitiationResult:
    """
    Result returned by a mobile-money provider after payment
    initiation.

    IMPORTANT:

        A successful initiation does NOT mean that the customer
        has successfully paid.

        It only means that the provider accepted the request
        for processing.
    """

    provider_reference: str
    status: str
    message: str = ""


@dataclass(frozen=True)
class PaymentVerificationResult:
    """
    Result returned by a mobile-money provider after independently
    verifying a payment.

    This result is used by PaymentVerificationService to determine
    whether the MovieTime Payment can be completed.
    """

    provider_reference: str
    status: str
    amount: Decimal
    currency: str