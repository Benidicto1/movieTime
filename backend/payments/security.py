# backend/payments/security.py

import hashlib
import hmac

from django.conf import settings


def generate_callback_signature(
    payload: bytes,
    secret: str,
) -> str:
    """
    Generate an HMAC-SHA256 signature for a payment-provider callback.

    Args:
        payload: Raw request body as bytes.
        secret: Shared callback secret.

    Returns:
        Hexadecimal HMAC-SHA256 signature.
    """
    if not secret:
        raise ValueError("Callback secret is required.")

    return hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()


def verify_callback_signature(
    *,
    payload: bytes,
    signature: str,
    secret: str,
) -> bool:
    """
    Verify an incoming payment-provider callback signature.

    Uses hmac.compare_digest() to avoid timing-based comparison attacks.

    Args:
        payload: Raw request body as bytes.
        signature: Signature supplied by the payment provider.
        secret: Shared callback secret.

    Returns:
        True if the signature is valid, otherwise False.
    """
    if not payload or not signature or not secret:
        return False

    expected_signature = generate_callback_signature(
        payload=payload,
        secret=secret,
    )

    return hmac.compare_digest(
        expected_signature,
        signature.strip(),
    )


def get_callback_secret(provider: str) -> str | None:
    """
    Get the configured callback secret for a payment provider.

    Provider-specific secrets should be stored in environment variables
    and loaded into Django settings.

    Supported providers:
        MTN
        AIRTEL

    Args:
        provider: Payment provider name.

    Returns:
        Configured callback secret or None.
    """
    if not provider:
        return None

    provider = provider.upper().strip()

    if provider == "MTN":
        return getattr(
            settings,
            "MTN_CALLBACK_SECRET",
            None,
        )

    if provider == "AIRTEL":
        return getattr(
            settings,
            "AIRTEL_CALLBACK_SECRET",
            None,
        )

    return None


def verify_provider_callback(
    *,
    provider: str,
    payload: bytes,
    signature: str,
) -> bool:
    """
    Verify a callback using the configured secret for the provider.

    This function provides a common interface for MTN and Airtel
    callback verification.

    IMPORTANT:
        The actual MTN/Airtel production authentication mechanism must
        follow the provider's official API documentation. This HMAC
        helper should not replace provider-specific authentication
        requirements when their API specifies a different mechanism.

    Args:
        provider: MTN or AIRTEL.
        payload: Raw HTTP request body.
        signature: Signature supplied with the callback.

    Returns:
        True when verification succeeds.
    """
    secret = get_callback_secret(provider)

    if not secret:
        return False

    return verify_callback_signature(
        payload=payload,
        signature=signature,
        secret=secret,
    )