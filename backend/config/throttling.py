
from rest_framework.throttling import SimpleRateThrottle


class AuthenticationRateThrottle(SimpleRateThrottle):
    """
    Rate limit authentication attempts by client IP address.

    This helps reduce brute-force login attempts.
    """

    scope = "authentication"

    def get_cache_key(self, request, view):
        ident = self.get_ident()

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class PaymentRateThrottle(SimpleRateThrottle):
    """
    Rate limit payment creation requests.

    Authenticated users are identified by their user ID.
    Anonymous requests fall back to IP address.
    """

    scope = "payment"

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = f"user:{request.user.pk}"
        else:
            ident = self.get_ident()

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class PurchaseRateThrottle(SimpleRateThrottle):
    """
    Rate limit purchase-related operations.

    Only authenticated users are throttled.
    """

    scope = "purchase"

    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None

        ident = f"user:{request.user.pk}"

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class DownloadRateThrottle(SimpleRateThrottle):
    """
    Rate limit download authorization and creation requests.

    The actual movie file transfer should be handled by
    object storage/CDN infrastructure rather than Django.
    """

    scope = "download"

    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None

        ident = f"user:{request.user.pk}"

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class StreamRateThrottle(SimpleRateThrottle):
    """
    Rate limit streaming authorization requests.

    This limits API authorization calls, not the video bandwidth
    itself.
    """

    scope = "stream"

    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None

        ident = f"user:{request.user.pk}"

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class PaymentStatusRateThrottle(SimpleRateThrottle):
    """
    Rate limit payment-status polling.

    This prevents the Android application or another client from
    repeatedly polling a payment-status endpoint at an excessive rate.
    """

    scope = "payment_status"

    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None

        ident = f"user:{request.user.pk}"

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }