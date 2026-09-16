# backend/payments/providers/airtel.py

from decimal import Decimal
from typing import Any

import requests
from django.conf import settings

from payments.exceptions import (
    PaymentConfigurationError,
    PaymentProviderError,
    PaymentVerificationError,
)
from payments.provider_result import (
    PaymentInitiationResult,
    PaymentVerificationResult,
)
from payments.providers.base import MobileMoneyProvider


class AirtelProvider(MobileMoneyProvider):
    """
    Airtel Money payment provider.

    This class implements the MovieTime provider interface for
    Airtel Money collections.

    Payment lifecycle:

        1. MovieTime creates a Payment.
        2. MovieTime requests an Airtel access token.
        3. MovieTime initiates the payment.
        4. Airtel processes the request.
        5. Customer approves/rejects the transaction.
        6. MovieTime verifies the transaction with Airtel.
        7. PaymentVerificationService completes the payment.

    IMPORTANT:

        Initiating a payment is NOT the same as completing a payment.

        MovieTime must never mark a payment as SUCCESS merely because
        Airtel accepted the initiation request.
    """

    provider_name = "AIRTEL"

    DEFAULT_TIMEOUT = 30

    TOKEN_PATH = "/auth/oauth2/token"

    COLLECTION_PATH = "/merchant/v1/payments/"

    STATUS_PATH = "/standard/v1/payments/{transaction_id}"

    def __init__(self):
        self.base_url = self._get_setting(
            "AIRTEL_BASE_URL"
        )

        self.client_id = self._get_setting(
            "AIRTEL_CLIENT_ID"
        )

        self.client_secret = self._get_setting(
            "AIRTEL_CLIENT_SECRET"
        )

        self.country = getattr(
            settings,
            "AIRTEL_COUNTRY",
            "UG",
        )

        self.currency = getattr(
            settings,
            "AIRTEL_CURRENCY",
            "UGX",
        )

        self.callback_url = getattr(
            settings,
            "AIRTEL_CALLBACK_URL",
            "",
        )

        self.timeout = getattr(
            settings,
            "AIRTEL_TIMEOUT",
            self.DEFAULT_TIMEOUT,
        )

        self._access_token = None

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    @staticmethod
    def _get_setting(name: str) -> str:
        """
        Get a required Airtel configuration value from Django settings.
        """

        value = getattr(settings, name, None)

        if not value:
            raise PaymentConfigurationError(
                f"Missing Airtel configuration: {name}"
            )

        return str(value).strip()

    def _validate_configuration(self) -> None:
        """
        Validate Airtel configuration before communicating with
        the provider.
        """

        required_values = {
            "AIRTEL_BASE_URL": self.base_url,
            "AIRTEL_CLIENT_ID": self.client_id,
            "AIRTEL_CLIENT_SECRET": self.client_secret,
        }

        missing = [
            name
            for name, value in required_values.items()
            if not value
        ]

        if missing:
            raise PaymentConfigurationError(
                "Missing Airtel configuration: "
                + ", ".join(missing)
            )

        if not self.country:
            raise PaymentConfigurationError(
                "AIRTEL_COUNTRY is required."
            )

        if not self.currency:
            raise PaymentConfigurationError(
                "AIRTEL_CURRENCY is required."
            )

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------

    def _build_url(self, path: str) -> str:
        """
        Build an absolute Airtel API URL.
        """

        base_url = self.base_url.rstrip("/")

        if not path.startswith("/"):
            path = "/" + path

        return f"{base_url}{path}"

    # ------------------------------------------------------------------
    # HTTP helper
    # ------------------------------------------------------------------

    def _request(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> requests.Response:
        """
        Execute an HTTP request against Airtel.

        requests-specific failures are converted into
        PaymentProviderError.
        """

        url = self._build_url(path)

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                data=data,
                timeout=self.timeout,
            )

        except requests.Timeout as exc:
            raise PaymentProviderError(
                "Airtel payment provider request timed out."
            ) from exc

        except requests.RequestException as exc:
            raise PaymentProviderError(
                "Unable to communicate with Airtel Money."
            ) from exc

        return response

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _get_access_token(self) -> str:
        """
        Obtain an OAuth access token from Airtel.

        The token is kept in memory for the lifetime of this
        provider instance.

        Production deployments should additionally account for
        token expiration and refresh/reacquisition.
        """

        self._validate_configuration()

        if self._access_token:
            return self._access_token

        headers = {
            "Content-Type": (
                "application/x-www-form-urlencoded"
            ),
            "Accept": "application/json",
        }

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        response = self._request(
            method="POST",
            path=self.TOKEN_PATH,
            headers=headers,
            data=data,
        )

        if response.status_code not in (200, 201):
            raise PaymentProviderError(
                self._extract_error_message(
                    response,
                    default=(
                        "Airtel access-token request failed."
                    ),
                )
            )

        try:
            response_data = response.json()
        except ValueError as exc:
            raise PaymentProviderError(
                "Airtel returned an invalid access-token response."
            ) from exc

        access_token = response_data.get(
            "access_token"
        )

        if not access_token:
            raise PaymentProviderError(
                "Airtel access-token response did not contain "
                "an access token."
            )

        self._access_token = str(
            access_token
        )

        return self._access_token

    # ------------------------------------------------------------------
    # Payment initiation
    # ------------------------------------------------------------------

    def initiate_payment(
        self,
        *,
        phone_number: str,
        amount: Decimal,
        currency: str,
        external_reference: str,
    ) -> PaymentInitiationResult:
        """
        Initiate an Airtel Money collection request.

        The returned transaction ID is stored by MovieTime as the
        provider reference.

        IMPORTANT:

            A successful HTTP response here only means that Airtel
            accepted the payment request.

            It does NOT mean the customer has successfully paid.
        """

        normalized_phone = self.normalize_phone_number(
            phone_number
        )

        normalized_amount = self.normalize_amount(
            amount
        )

        normalized_currency = self.normalize_currency(
            currency
        )

        normalized_external_reference = (
            self.validate_external_reference(
                external_reference
            )
        )

        access_token = self._get_access_token()

        headers = {
            "Authorization": (
                f"Bearer {access_token}"
            ),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Country": self.country,
            "X-Currency": normalized_currency,
        }

        payload = {
            "reference": normalized_external_reference,
            "subscriber": {
                "country": self.country,
                "currency": normalized_currency,
                "msisdn": normalized_phone,
            },
            "transaction": {
                "amount": str(
                    normalized_amount
                ),
                "country": self.country,
                "currency": normalized_currency,
                "id": normalized_external_reference,
            },
        }

        if self.callback_url:
            payload["transaction"]["callback_url"] = (
                self.callback_url
            )

        response = self._request(
            method="POST",
            path=self.COLLECTION_PATH,
            headers=headers,
            json=payload,
        )

        if response.status_code not in (
            200,
            201,
            202,
        ):
            raise PaymentProviderError(
                self._extract_error_message(
                    response,
                    default=(
                        "Airtel did not accept the payment "
                        "request."
                    ),
                )
            )

        try:
            response_data = response.json()
        except ValueError as exc:
            raise PaymentProviderError(
                "Airtel returned an invalid payment-initiation "
                "response."
            ) from exc

        provider_reference = (
            self._extract_transaction_reference(
                response_data
            )
        )

        if not provider_reference:
            raise PaymentProviderError(
                "Airtel payment response did not contain "
                "a transaction reference."
            )

        status_value = (
            self._extract_status(
                response_data
            )
        )

        return PaymentInitiationResult(
            provider_reference=provider_reference,
            status=status_value or "PROCESSING",
            message=(
                "Airtel Money payment request accepted. "
                "Waiting for customer approval."
            ),
        )

    # ------------------------------------------------------------------
    # Payment verification
    # ------------------------------------------------------------------

    def verify_payment(
        self,
        *,
        provider_reference: str,
        external_reference: str | None = None,
    ) -> PaymentVerificationResult:
        """
        Verify the current state of an Airtel Money transaction.

        MovieTime uses this response to independently determine
        whether the transaction should be completed.
        """

        if not provider_reference:
            raise PaymentVerificationError(
                "Airtel provider reference is required."
            )

        provider_reference = provider_reference.strip()

        access_token = self._get_access_token()

        headers = {
            "Authorization": (
                f"Bearer {access_token}"
            ),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Country": self.country,
            "X-Currency": self.currency,
        }

        path = self.STATUS_PATH.format(
            transaction_id=provider_reference
        )

        response = self._request(
            method="GET",
            path=path,
            headers=headers,
        )

        if response.status_code != 200:
            raise PaymentVerificationError(
                self._extract_error_message(
                    response,
                    default=(
                        "Airtel payment status verification failed."
                    ),
                )
            )

        try:
            response_data = response.json()
        except ValueError as exc:
            raise PaymentVerificationError(
                "Airtel returned an invalid payment-status "
                "response."
            ) from exc

        status_value = self._extract_status(
            response_data
        )

        if not status_value:
            raise PaymentVerificationError(
                "Airtel payment-status response did not "
                "contain a transaction status."
            )

        amount_value = self._extract_amount(
            response_data
        )

        if amount_value is None:
            raise PaymentVerificationError(
                "Airtel payment-status response did not "
                "contain a transaction amount."
            )

        try:
            verified_amount = Decimal(
                str(amount_value)
            )
        except Exception as exc:
            raise PaymentVerificationError(
                "Airtel returned an invalid transaction amount."
            ) from exc

        verified_currency = self._extract_currency(
            response_data
        )

        if not verified_currency:
            raise PaymentVerificationError(
                "Airtel payment-status response did not "
                "contain a transaction currency."
            )

        verified_reference = (
            self._extract_transaction_reference(
                response_data
            )
            or provider_reference
        )

        return PaymentVerificationResult(
            provider_reference=str(
                verified_reference
            ),
            status=status_value,
            amount=verified_amount,
            currency=verified_currency,
        )

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_transaction_reference(
        data: dict[str, Any],
    ) -> str | None:
        """
        Extract a transaction reference from Airtel's response.

        Airtel API response structures can vary between API products
        and account configurations, so this parser accepts the common
        reference locations.
        """

        transaction = data.get(
            "transaction"
        )

        if isinstance(transaction, dict):
            for key in (
                "id",
                "transaction_id",
                "transactionId",
                "reference",
            ):
                value = transaction.get(key)

                if value:
                    return str(value)

        for key in (
            "transaction_id",
            "transactionId",
            "reference",
            "id",
        ):
            value = data.get(key)

            if value:
                return str(value)

        data_section = data.get("data")

        if isinstance(data_section, dict):
            for key in (
                "transaction_id",
                "transactionId",
                "reference",
                "id",
            ):
                value = data_section.get(key)

                if value:
                    return str(value)

        return None

    @staticmethod
    def _extract_status(
        data: dict[str, Any],
    ) -> str:
        """
        Extract and normalize the provider transaction status.
        """

        candidates = []

        transaction = data.get(
            "transaction"
        )

        if isinstance(transaction, dict):
            candidates.extend(
                [
                    transaction.get("status"),
                    transaction.get("transaction_status"),
                ]
            )

        candidates.extend(
            [
                data.get("status"),
                data.get("transaction_status"),
                data.get("transactionStatus"),
            ]
        )

        data_section = data.get("data")

        if isinstance(data_section, dict):
            candidates.extend(
                [
                    data_section.get("status"),
                    data_section.get(
                        "transaction_status"
                    ),
                ]
            )

        for value in candidates:
            if value:
                return str(value).strip().upper()

        return ""

    @staticmethod
    def _extract_amount(
        data: dict[str, Any],
    ) -> Any:
        """
        Extract the transaction amount.
        """

        transaction = data.get(
            "transaction"
        )

        if isinstance(transaction, dict):
            for key in (
                "amount",
                "transaction_amount",
            ):
                value = transaction.get(key)

                if value is not None:
                    return value

        for key in (
            "amount",
            "transaction_amount",
        ):
            value = data.get(key)

            if value is not None:
                return value

        data_section = data.get("data")

        if isinstance(data_section, dict):
            for key in (
                "amount",
                "transaction_amount",
            ):
                value = data_section.get(key)

                if value is not None:
                    return value

        return None

    @staticmethod
    def _extract_currency(
        data: dict[str, Any],
    ) -> str:
        """
        Extract and normalize the transaction currency.
        """

        transaction = data.get(
            "transaction"
        )

        if isinstance(transaction, dict):
            for key in (
                "currency",
            ):
                value = transaction.get(key)

                if value:
                    return str(value).strip().upper()

        for key in (
            "currency",
        ):
            value = data.get(key)

            if value:
                return str(value).strip().upper()

        data_section = data.get("data")

        if isinstance(data_section, dict):
            value = data_section.get(
                "currency"
            )

            if value:
                return str(value).strip().upper()

        return ""

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_error_message(
        response: requests.Response,
        *,
        default: str,
    ) -> str:
        """
        Extract a safe provider error message.

        Authentication headers, client secrets, and other sensitive
        information are never returned to the caller.
        """

        try:
            data = response.json()
        except ValueError:
            data = None

        if isinstance(data, dict):

            for key in (
                "message",
                "error",
                "error_description",
                "status",
            ):
                value = data.get(key)

                if value:
                    return (
                        f"{default} "
                        f"Provider response: {value}"
                    )

            error_data = data.get(
                "error"
            )

            if isinstance(error_data, dict):
                for key in (
                    "message",
                    "description",
                    "code",
                ):
                    value = error_data.get(key)

                    if value:
                        return (
                            f"{default} "
                            f"Provider response: {value}"
                        )

        return default