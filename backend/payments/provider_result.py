# backend/payments/provider_result.py

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PaymentInitiationResult:
    """
    Result returned by a mobile-money provider after payment
    initiation.

    IMPORTANT:

    Successful initiation does NOT mean that the customer
    successfully paid.

    It only means that the provider accepted the payment
    request for processing.
    """

    provider_reference: str
    status: str
    message: str = ""


@dataclass(frozen=True)
class PaymentVerificationResult:
    """
    Result returned by a mobile-money provider after independently
    verifying a payment.

    PaymentVerificationService uses this result to determine
    whether the MovieTime payment can be completed.
    """

    provider_reference: str
    status: str
    amount: Decimal
    currency: str