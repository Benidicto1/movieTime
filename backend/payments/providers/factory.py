from .airtel import AirtelPaymentProvider
from .mtn import MTNPaymentProvider


def get_payment_provider(provider):

    if provider == "MTN":
        return MTNPaymentProvider()

    if provider == "AIRTEL":
        return AirtelPaymentProvider()

    raise ValueError(
        f"Unsupported payment provider: {provider}"
    )