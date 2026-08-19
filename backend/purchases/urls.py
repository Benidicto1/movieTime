from django.urls import path

from .views import (
    PurchaseCreateAPIView,
    PurchaseListAPIView,
)


urlpatterns = [
    path(
        "purchases/",
        PurchaseListAPIView.as_view(),
        name="purchase-list",
    ),

    path(
        "purchases/create/",
        PurchaseCreateAPIView.as_view(),
        name="purchase-create",
    ),
]