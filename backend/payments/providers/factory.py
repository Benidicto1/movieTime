# backend/payments/providers/factory.py

from payments.exceptions import PaymentConfigurationError
from payments.models import Payment
from payments.providers.airtel import AirtelProvider
from payments.providers.base import MobileMoneyProvider
from payments.providers.mtn import MTNProvider


class PaymentProviderFactory:
    """
    Factory responsible for creating the correct mobile-money
    provider implementation.

    Supported providers:

        MTN
        AIRTEL

    The factory does not:

        - create Payment records
        - initiate transactions
        - verify transactions
        - mark payments as successful
        - activate subscriptions
        - grant movie ownership

    Those responsibilities belong to PaymentService and
    PaymentVerificationService.
    """

    _providers = {
        Payment.Provider.MTN: MTNProvider,
        Payment.Provider.AIRTEL: AirtelProvider,
    }

    @classmethod
    def get_provider(
        cls,
        provider: str,
    ) -> MobileMoneyProvider:
        """
        Return an instance of the requested payment provider.

        Args:
            provider:
                Provider identifier, for example:

                    MTN
                    AIRTEL

        Returns:
            MobileMoneyProvider instance.

        Raises:
            PaymentConfigurationError:
                If the requested provider is unsupported.
        """

        if not provider:
            raise PaymentConfigurationError(
                "Payment provider is required."
            )

        normalized_provider = str(
            provider
        ).strip().upper()

        provider_class = cls._providers.get(
            normalized_provider
        )

        if provider_class is None:
            raise PaymentConfigurationError(
                f"Unsupported payment provider: "
                f"{normalized_provider}"
            )

        try:
            provider_instance = provider_class()

        except PaymentConfigurationError:
            raise

        except Exception as exc:
            raise PaymentConfigurationError(
                f"Unable to initialize payment provider: "
                f"{normalized_provider}"
            ) from exc

        if not isinstance(
            provider_instance,
            MobileMoneyProvider,
        ):
            raise PaymentConfigurationError(
                f"Payment provider "
                f"{normalized_provider} does not implement "
                f"MobileMoneyProvider."
            )

        return provider_instance

    @classmethod
    def is_supported(
        cls,
        provider: str,
    ) -> bool:
        """
        Check whether a payment provider is supported.

        This method does not initialize the provider and therefore
        does not require provider credentials to be configured.
        """

        if not provider:
            return False

        normalized_provider = str(
            provider
        ).strip().upper()

        return normalized_provider in cls._providers

    @classmethod
    def supported_providers(
        cls,
    ) -> tuple[str, ...]:
        """
        Return all supported provider identifiers.
        """

        return tuple(
            cls._providers.keys()
        )