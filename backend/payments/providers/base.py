# backend/payments/providers/base.py

from abc import ABC, abstractmethod
from decimal import Decimal

from payments.provider_result import (
    PaymentInitiationResult,
    PaymentVerificationResult,
)


class MobileMoneyProvider(ABC):
    """
    Abstract interface for MovieTime mobile-money providers.

    Concrete providers such as MTN and Airtel must implement
    the methods defined here.

    IMPORTANT:

        Initiating a payment does NOT mean that the payment
        was successfully completed.

    Normal lifecycle:

        1. MovieTime creates a Payment.
        2. MovieTime sends a payment request to the provider.
        3. Provider accepts or rejects the request.
        4. Customer approves the payment.
        5. MovieTime verifies the final provider status.
        6. Only then is the MovieTime Payment marked SUCCESS.
    """

    provider_name = None

    @abstractmethod
    def initiate_payment(
        self,
        *,
        phone_number: str,
        amount: Decimal,
        currency: str,
        external_reference: str,
    ) -> PaymentInitiationResult:
        """
        Initiate a mobile-money payment request.

        This method only starts the provider transaction.

        It MUST NOT assume that the customer has successfully
        paid merely because the provider accepted the request.

        Args:
            phone_number:
                Uganda mobile-money number in normalized format.

            amount:
                Amount that the customer is expected to pay.

            currency:
                Payment currency, normally UGX.

            external_reference:
                MovieTime's unique payment reference.

        Returns:
            PaymentInitiationResult containing the provider
            transaction reference and initial provider status.

        Raises:
            PaymentProviderError:
                When the provider cannot be contacted or returns
                an unusable response.

            PaymentConfigurationError:
                When required provider credentials/configuration
                are missing.
        """
        raise NotImplementedError

    @abstractmethod
    def verify_payment(
        self,
        *,
        provider_reference: str,
        external_reference: str | None = None,
    ) -> PaymentVerificationResult:
        """
        Verify the final state of a payment with the provider.

        MovieTime must independently verify the payment before
        granting ownership, activating a subscription, or
        marking the Payment as SUCCESS.

        Args:
            provider_reference:
                Transaction/reference returned by the provider
                during payment initiation.

            external_reference:
                MovieTime's own payment reference, when supported
                by the provider.

        Returns:
            PaymentVerificationResult containing:

                - provider reference
                - provider status
                - verified amount
                - verified currency

        Raises:
            PaymentProviderError:
                When the provider cannot be contacted.

            PaymentVerificationError:
                When the provider response cannot be trusted
                or required information is missing.
        """
        raise NotImplementedError

    def normalize_phone_number(
        self,
        phone_number: str,
    ) -> str:
        """
        Normalize a Ugandan mobile-money phone number.

        The payment layer expects the canonical international
        format:

            2567XXXXXXXX

        Examples:

            0771234567
            +256771234567
            256771234567

        All are normalized to:

            256771234567

        This helper does not replace serializer validation.
        It provides an additional normalization layer before
        communicating with a provider.
        """

        if not phone_number:
            raise ValueError(
                "Phone number is required."
            )

        phone_number = str(
            phone_number
        ).strip()

        if phone_number.startswith("+"):
            phone_number = phone_number[1:]

        if phone_number.startswith("0"):
            phone_number = (
                "256" + phone_number[1:]
            )

        if not phone_number.startswith("256"):
            raise ValueError(
                "Phone number must use Ugandan international format."
            )

        if len(phone_number) != 12:
            raise ValueError(
                "Invalid Ugandan phone number length."
            )

        if not phone_number.startswith("2567"):
            raise ValueError(
                "Invalid Ugandan mobile-money phone number."
            )

        if not phone_number.isdigit():
            raise ValueError(
                "Phone number must contain digits only."
            )

        return phone_number

    def normalize_currency(
        self,
        currency: str,
    ) -> str:
        """
        Normalize a payment currency code.

        MovieTime currently expects UGX for Ugandan
        mobile-money transactions.
        """

        if not currency:
            raise ValueError(
                "Currency is required."
            )

        normalized_currency = str(
            currency
        ).strip().upper()

        if len(normalized_currency) != 3:
            raise ValueError(
                "Currency must be a three-letter ISO code."
            )

        return normalized_currency

    def normalize_amount(
        self,
        amount: Decimal,
    ) -> Decimal:
        """
        Normalize and validate the payment amount.

        The amount is determined by the MovieTime backend.

        This method only validates the value before it is
        sent to a provider.
        """

        if amount is None:
            raise ValueError(
                "Payment amount is required."
            )

        try:
            normalized_amount = Decimal(
                str(amount)
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Invalid payment amount."
            ) from exc

        if normalized_amount <= Decimal("0"):
            raise ValueError(
                "Payment amount must be greater than zero."
            )

        return normalized_amount

    def validate_external_reference(
        self,
        external_reference: str,
    ) -> str:
        """
        Validate MovieTime's payment reference before sending
        it to a provider.
        """

        if not external_reference:
            raise ValueError(
                "External payment reference is required."
            )

        normalized_reference = str(
            external_reference
        ).strip()

        if not normalized_reference:
            raise ValueError(
                "External payment reference cannot be empty."
            )

        # IMPORTANT:
        # Do not add a trailing comma here.
        #
        # `return normalized_reference,`
        # would return a tuple instead of a string.
        return normalized_reference