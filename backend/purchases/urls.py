"""
MovieTime purchase URL configuration.

Chapter 78 — Abuse Prevention
"""

from django.urls import path

from .views import (
    PurchaseCreateAPIView,
    PurchaseDetailAPIView,
    PurchaseListAPIView,
    PurchaseOwnershipAPIView,
)


app_name = "purchases"


urlpatterns = [
    # ---------------------------------------------------------
    # Purchase list
    # ---------------------------------------------------------

    path(
        "purchases/",
        PurchaseListAPIView.as_view(),
        name="purchase-list",
    ),

    # ---------------------------------------------------------
    # Create pending purchase
    # ---------------------------------------------------------

    path(
        "purchases/create/",
        PurchaseCreateAPIView.as_view(),
        name="purchase-create",
    ),

    # ---------------------------------------------------------
    # Purchase detail
    # ---------------------------------------------------------

    path(
        "purchases/<int:purchase_id>/",
        PurchaseDetailAPIView.as_view(),
        name="purchase-detail",
    ),

    # ---------------------------------------------------------
    # Movie ownership
    # ---------------------------------------------------------

    path(
        "purchases/movie/<int:movie_id>/ownership/",
        PurchaseOwnershipAPIView.as_view(),
        name="purchase-ownership",
    ),
]