from abc import ABC, abstractmethod


class MobileMoneyProvider(ABC):
    """
    Base interface for MovieTime mobile money
    payment providers.
    """

    @abstractmethod
    def initiate_payment(
        self,
        *,
        amount,
        currency,
        phone_number,
        reference,
    ):
        """
        Start a mobile money payment.
        """
        raise NotImplementedError
