from .airtel import AirtelMoneyProvider
from .mtn import MTNMobileMoneyProvider


def get_payment_provider(
    provider,
):
    """
    Return the correct mobile money provider.
    """

    provider = provider.upper()

    if provider == "MTN":
        return MTNMobileMoneyProvider()

    if provider == "AIRTEL":
        return AirtelMoneyProvider()

    raise ValueError(
        "Unsupported payment provider."
    )
