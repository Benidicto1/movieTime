import requests

from django.conf import settings

from .base import PaymentProvider


class MTNPaymentProvider(PaymentProvider):

    def __init__(self):
        self.base_url = settings.MTN_BASE_URL
        self.api_user = settings.MTN_API_USER
        self.api_key = settings.MTN_API_KEY
        self.subscription_key = (
            settings.MTN_SUBSCRIPTION_KEY
        )

    def initiate_payment(
        self,
        *,
        payment,
        phone_number,
    ):
        """
        Initiate an MTN Mobile Money payment.
        """

        raise NotImplementedError(
            "MTN payment initiation will be implemented "
            "after configuring the MTN API."
        )

    def verify_payment(
        self,
        *,
        payment,
    ):
        """
        Verify the payment with MTN.
        """

        raise NotImplementedError(
            "MTN payment verification will be implemented "
            "after configuring the MTN API."
        )