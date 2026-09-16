# backend/payments/providers/mtn.py

import uuid
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


class MTNProvider(MobileMoneyProvider):
    """
    MTN Mobile Money Collections provider.

    This provider implements the MTN MoMo Request-to-Pay flow.

    Flow:

        MovieTime
            |
            | 1. Get OAuth access token
            v
        MTN API
            |
            | 2. POST /requesttopay
            v
        MTN Wallet
            |
            | 3. Customer approves/rejects
            v
        MTN
            |
            | 4. Callback or status polling
            v
        MovieTime
            |
            | 5. Independently verify transaction
            v
        PaymentService
            |
            | 6. Mark payment SUCCESS
            v
        Purchase / Subscription

    IMPORTANT:

        A 202 response from MTN means the request was accepted
        for processing. It does NOT mean that the customer paid.

        Final payment success must come from provider verification.
    """

    provider_name = "MTN"

    DEFAULT_TIMEOUT = 30

    TOKEN_PATH = "/collection/token/"

    REQUEST_TO_PAY_PATH = "/collection/v1_0/requesttopay"

    REQUEST_TO_PAY_STATUS_PATH = (
        "/collection/v1_0/requesttopay/{reference_id}"
    )

    def __init__(self):
        self.base_url = self._get_setting(
            "MTN_MOMO_BASE_URL"
        )

        self.api_user = self._get_setting(
            "MTN_MOMO_API_USER"
        )

        self.api_key = self._get_setting(
            "MTN_MOMO_API_KEY"
        )

        self.subscription_key = self._get_setting(
            "MTN_MOMO_SUBSCRIPTION_KEY"
        )

        self.target_environment = getattr(
            settings,
            "MTN_MOMO_TARGET_ENVIRONMENT",
            "sandbox",
        )

        self.callback_url = getattr(
            settings,
            "MTN_MOMO_CALLBACK_URL",
            "",
        )

        self.timeout = getattr(
            settings,
            "MTN_MOMO_TIMEOUT",
            self.DEFAULT_TIMEOUT,
        )

        self._access_token = None

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    @staticmethod
    def _get_setting(name: str) -> str:
        """
        Read a required MTN configuration value from Django settings.
        """

        value = getattr(settings, name, None)

        if not value:
            raise PaymentConfigurationError(
                f"Missing MTN configuration: {name}"
            )

        return str(value).strip()

    def _validate_configuration(self) -> None:
        """
        Validate required MTN configuration before communicating
        with the provider.
        """

        required_values = {
            "MTN_MOMO_BASE_URL": self.base_url,
            "MTN_MOMO_API_USER": self.api_user,
            "MTN_MOMO_API_KEY": self.api_key,
            "MTN_MOMO_SUBSCRIPTION_KEY": self.subscription_key,
        }

        missing = [
            name
            for name, value in required_values.items()
            if not value
        ]

        if missing:
            raise PaymentConfigurationError(
                "Missing MTN configuration: "
                + ", ".join(missing)
            )

        if not self.target_environment:
            raise PaymentConfigurationError(
                "MTN_MOMO_TARGET_ENVIRONMENT is required."
            )

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------

    def _build_url(self, path: str) -> str:
        """
        Build an absolute MTN API URL.
        """

        base_url = self.base_url.rstrip("/")

        if not path.startswith("/"):
            path = "/" + path

        return f"{base_url}{path}"

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _request(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        auth: tuple[str, str] | None = None,
    ) -> requests.Response:
        """
        Execute an HTTP request against MTN.

        Provider communication errors are converted into
        PaymentProviderError so the payment service does not
        need to understand requests-specific exceptions.
        """

        url = self._build_url(path)

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                auth=auth,
                timeout=self.timeout,
            )

        except requests.Timeout as exc:
            raise PaymentProviderError(
                "MTN payment provider request timed out."
            ) from exc

        except requests.RequestException as exc:
            raise PaymentProviderError(
                "Unable to communicate with MTN Mobile Money."
            ) from exc

        return response

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _get_access_token(self) -> str:
        """
        Obtain an OAuth access token from MTN.

        MTN's MoMo API requires an access token before calling
        Collections endpoints.
        """

        self._validate_configuration()

        if self._access_token:
            return self._access_token

        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json",
            "X-Target-Environment": self.target_environment,
        }

        response = self._request(
            method="POST",
            path=self.TOKEN_PATH,
            headers=headers,
            auth=(
                self.api_user,
                self.api_key,
            ),
        )

        if response.status_code != 200:
            raise PaymentProviderError(
                self._extract_error_message(
                    response,
                    default=(
                        "MTN access-token request failed."
                    ),
                )
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise PaymentProviderError(
                "MTN returned an invalid access-token response."
            ) from exc

        access_token = data.get("access_token")

        if not access_token:
            raise PaymentProviderError(
                "MTN access-token response did not contain "
                "an access token."
            )

        self._access_token = str(access_token)

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
        Start an MTN Request-to-Pay transaction.

        IMPORTANT:

            HTTP 202 means MTN accepted the request.

            It does NOT mean the customer successfully paid.

        The returned UUID is stored as provider_reference and is
        later used to verify the transaction.
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

        # MTN Request-to-Pay requires a UUID v4 reference.
        provider_reference = str(
            uuid.uuid4()
        )

        headers = {
            "Authorization": (
                f"Bearer {access_token}"
            ),
            "Ocp-Apim-Subscription-Key": (
                self.subscription_key
            ),
            "X-Target-Environment": (
                self.target_environment
            ),
            "X-Reference-Id": provider_reference,
            "Content-Type": "application/json",
        }

        payload = {
            "amount": str(
                normalized_amount
            ),
            "currency": normalized_currency,
            "externalId": normalized_external_reference,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": normalized_phone,
            },
            "payerMessage": (
                "MovieTime payment"
            ),
            "payeeNote": (
                f"MovieTime payment "
                f"{normalized_external_reference}"
            ),
        }

        if self.callback_url:
            payload["callbackUrl"] = self.callback_url

        response = self._request(
            method="POST",
            path=self.REQUEST_TO_PAY_PATH,
            headers=headers,
            json=payload,
        )

        if response.status_code != 202:
            raise PaymentProviderError(
                self._extract_error_message(
                    response,
                    default=(
                        "MTN did not accept the payment "
                        "request."
                    ),
                )
            )

        return PaymentInitiationResult(
            provider_reference=provider_reference,
            status="PROCESSING",
            message=(
                "MTN payment request accepted. "
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
        Query MTN for the current status of a Request-to-Pay
        transaction.

        This method independently verifies:

            - provider reference
            - transaction status
            - amount
            - currency

        The PaymentVerificationResult is then consumed by
        PaymentVerificationService.
        """

        if not provider_reference:
            raise PaymentVerificationError(
                "MTN provider reference is required."
            )

        provider_reference = provider_reference.strip()

        access_token = self._get_access_token()

        headers = {
            "Authorization": (
                f"Bearer {access_token}"
            ),
            "Ocp-Apim-Subscription-Key": (
                self.subscription_key
            ),
            "X-Target-Environment": (
                self.target_environment
            ),
            "Content-Type": "application/json",
        }

        path = self.REQUEST_TO_PAY_STATUS_PATH.format(
            reference_id=provider_reference
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
                        "MTN payment status verification failed."
                    ),
                )
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise PaymentVerificationError(
                "MTN returned an invalid payment-status response."
            ) from exc

        response_reference = (
            data.get("referenceId")
            or data.get("financialTransactionId")
            or provider_reference
        )

        status_value = str(
            data.get("status", "")
        ).strip().upper()

        if not status_value:
            raise PaymentVerificationError(
                "MTN payment-status response did not "
                "contain a transaction status."
            )

        amount_value = data.get("amount")

        if amount_value is None:
            raise PaymentVerificationError(
                "MTN payment-status response did not "
                "contain a transaction amount."
            )

        try:
            verified_amount = Decimal(
                str(amount_value)
            )
        except Exception as exc:
            raise PaymentVerificationError(
                "MTN returned an invalid transaction amount."
            ) from exc

        verified_currency = str(
            data.get("currency", "")
        ).strip().upper()

        if not verified_currency:
            raise PaymentVerificationError(
                "MTN payment-status response did not "
                "contain a transaction currency."
            )

        return PaymentVerificationResult(
            provider_reference=str(
                response_reference
            ),
            status=status_value,
            amount=verified_amount,
            currency=verified_currency,
        )

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
        Safely extract a useful error message from an MTN response.

        Avoid returning credentials, authorization headers,
        or complete provider responses to the client.
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
                "code",
            ):
                value = data.get(key)

                if value:
                    return (
                        f"{default} "
                        f"Provider response: {value}"
                    )

        return default