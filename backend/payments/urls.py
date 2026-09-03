from django.urls import path

from .views import (
    PaymentStatusAPIView,
    PurchasePaymentAPIView,
    SubscriptionPaymentAPIView,
)


urlpatterns = [

    path(
        "subscriptions/",
        SubscriptionPaymentAPIView.as_view(),
        name="subscription-payment",
    ),

    path(
        "purchases/",
        PurchasePaymentAPIView.as_view(),
        name="purchase-payment",
    ),

    path(
        "<int:payment_id>/status/",
        PaymentStatusAPIView.as_view(),
        name="payment-status",
    ),
]