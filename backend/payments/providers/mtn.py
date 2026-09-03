from .base import MobileMoneyProvider


class MTNMobileMoneyProvider(
    MobileMoneyProvider
):
    """
    MTN Mobile Money provider.

    The real MTN API integration will be added
    when the backend payment provider configuration
    is implemented.
    """

    def initiate_payment(
        self,
        *,
        amount,
        currency,
        phone_number,
        reference,
    ):
        raise NotImplementedError(
            "MTN Mobile Money integration "
            "has not been configured yet."
        )