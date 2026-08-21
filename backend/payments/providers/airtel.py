from django.conf import settings

from .base import PaymentProvider


class AirtelPaymentProvider(PaymentProvider):

    def __init__(self):
        self.base_url = settings.AIRTEL_BASE_URL
        self.client_id = settings.AIRTEL_CLIENT_ID
        self.client_secret = settings.AIRTEL_CLIENT_SECRET

    def initiate_payment(
        self,
        *,
        payment,
        phone_number,
    ):
        """
        Initiate an Airtel Money payment.
        """

        raise NotImplementedError(
            "Airtel payment initiation will be "
            "implemented after configuring the "
            "Airtel Money API."
        )

    def verify_payment(
        self,
        *,
        payment,
    ):
        """
        Verify the payment with Airtel.
        """

        raise NotImplementedError(
            "Airtel payment verification will be "
            "implemented after configuring the "
            "Airtel Money API."
        )