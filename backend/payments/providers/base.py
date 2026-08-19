from abc import ABC, abstractmethod


class PaymentProvider(ABC):

    @abstractmethod
    def initiate_payment(
        self,
        *,
        payment,
        phone_number,
    ):
        pass

    @abstractmethod
    def verify_payment(
        self,
        *,
        payment,
    ):
        pass