"""
MovieTime purchase API views.

Chapter 78 — Abuse Prevention

Purchase endpoints are protected with dedicated throttling
and object-level authorization.

Security rules:
- Movie prices are determined by the server.
- Users can only access their own purchases.
- A purchase becomes permanent ownership only after payment
  has successfully been verified.
- Clients cannot mark purchases as PAID.
- Duplicate pending purchases are prevented.
"""

from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.abuse_prevention import (
    AbusePreventionService,
    InvalidOperationError,
)
from config.throttling import PurchaseRateThrottle

from movies.models import Movie

from .models import Purchase
from .services import PurchaseService


# ============================================================
# RESPONSE HELPERS
# ============================================================


def purchase_to_dict(purchase):
    """
    Convert a Purchase object into a safe API response.
    """

    return {
        "id": purchase.id,
        "movie_id": purchase.movie_id,
        "amount": str(purchase.amount),
        "currency": purchase.currency,
        "status": purchase.status,
        "is_owned": purchase.is_owned,
        "created_at": purchase.created_at,
        "paid_at": purchase.paid_at,
    }


# ============================================================
# CREATE PURCHASE
# ============================================================


class PurchaseCreateAPIView(APIView):
    """
    Create a pending movie purchase.

    POST /api/v1/purchases/create/

    Expected request:

    {
        "movie_id": 123
    }

    The movie price is always obtained from the backend.
    The client cannot submit the purchase price.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    throttle_classes = [
        PurchaseRateThrottle,
    ]

    def post(self, request):
        """
        Create a pending purchase.
        """

        movie_id = request.data.get("movie_id")

        # ----------------------------------------------------
        # Validate movie ID
        # ----------------------------------------------------

        try:
            movie_id = (
                AbusePreventionService
                .normalize_identifier(movie_id)
            )

        except InvalidOperationError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Find movie
        # ----------------------------------------------------

        try:
            movie = Movie.objects.get(
                id=movie_id,
                is_active=True,
            )

        except Movie.DoesNotExist:
            return Response(
                {
                    "detail": "Movie not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------------------------------
        # Check permanent ownership
        # ----------------------------------------------------

        existing_paid_purchase = (
            Purchase.objects
            .filter(
                user=request.user,
                movie=movie,
                status=Purchase.Status.PAID,
            )
            .first()
        )

        if existing_paid_purchase:
            return Response(
                {
                    "detail": "You already own this movie.",
                    "purchase": purchase_to_dict(
                        existing_paid_purchase
                    ),
                },
                status=status.HTTP_200_OK,
            )

        # ----------------------------------------------------
        # Create pending purchase through service layer
        # ----------------------------------------------------

        try:
            purchase = (
                PurchaseService
                .create_pending_purchase(
                    user=request.user,
                    movie=movie,
                )
            )

        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Existing pending purchase
        # ----------------------------------------------------

        if purchase.status == Purchase.Status.PENDING:
            return Response(
                {
                    "purchase": purchase_to_dict(
                        purchase
                    ),
                },
                status=status.HTTP_200_OK,
            )

        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        return Response(
            {
                "purchase": purchase_to_dict(
                    purchase
                ),
            },
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# PURCHASE LIST
# ============================================================


class PurchaseListAPIView(APIView):
    """
    Return purchases belonging to the authenticated user.

    GET /api/v1/purchases/
    """

    permission_classes = [
        IsAuthenticated,
    ]

    throttle_classes = [
        PurchaseRateThrottle,
    ]

    def get(self, request):
        """
        Return the authenticated user's purchases.
        """

        purchases = (
            Purchase.objects
            .filter(
                user=request.user,
            )
            .select_related(
                "movie",
            )
            .order_by(
                "-created_at",
            )
        )

        results = [
            purchase_to_dict(purchase)
            for purchase in purchases
        ]

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# PURCHASE DETAIL
# ============================================================


class PurchaseDetailAPIView(APIView):
    """
    Retrieve one purchase belonging to the authenticated user.

    GET /api/v1/purchases/<purchase_id>/
    """

    permission_classes = [
        IsAuthenticated,
    ]

    throttle_classes = [
        PurchaseRateThrottle,
    ]

    def get(self, request, purchase_id):
        """
        Return purchase information.
        """

        try:
            purchase_id = (
                AbusePreventionService
                .normalize_identifier(purchase_id)
            )

        except InvalidOperationError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            purchase = (
                Purchase.objects
                .select_related("movie")
                .get(
                    id=purchase_id,
                )
            )

        except Purchase.DoesNotExist:
            return Response(
                {
                    "detail": "Purchase not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------------------------------
        # Object-level authorization
        # ----------------------------------------------------

        if purchase.user_id != request.user.id:
            return Response(
                {
                    "detail": "Purchase not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            purchase_to_dict(purchase),
            status=status.HTTP_200_OK,
        )


# ============================================================
# PURCHASE OWNERSHIP
# ============================================================


class PurchaseOwnershipAPIView(APIView):
    """
    Check whether the authenticated user permanently owns
    a particular movie.

    GET /api/v1/purchases/movie/<movie_id>/ownership/
    """

    permission_classes = [
        IsAuthenticated,
    ]

    throttle_classes = [
        PurchaseRateThrottle,
    ]

    def get(self, request, movie_id):
        """
        Return permanent ownership status.
        """

        try:
            movie_id = (
                AbusePreventionService
                .normalize_identifier(movie_id)
            )

        except InvalidOperationError as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        purchase = (
            Purchase.objects
            .filter(
                user=request.user,
                movie_id=movie_id,
                status=Purchase.Status.PAID,
            )
            .first()
        )

        if purchase is None:
            return Response(
                {
                    "movie_id": movie_id,
                    "owned": False,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "movie_id": purchase.movie_id,
                "owned": True,
                "purchase_id": purchase.id,
                "purchased_at": purchase.paid_at,
            },
            status=status.HTTP_200_OK,
        )