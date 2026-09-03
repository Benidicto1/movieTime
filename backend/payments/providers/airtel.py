from .base import MobileMoneyProvider


class AirtelMoneyProvider(
    MobileMoneyProvider
):
    """
    Airtel Money provider.

    The real Airtel API integration will be added
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
            "Airtel Money integration "
            "has not been configured yet."
        )
