from django.urls import path

from payments.views import (
    PaymentStatusAPIView,
    PaymentVerificationAPIView,
    PurchasePaymentAPIView,
    SubscriptionPaymentAPIView,
)


app_name = "payments"


urlpatterns = [
    path(
        "purchases/",
        PurchasePaymentAPIView.as_view(),
        name="purchase-payment",
    ),

    path(
        "subscriptions/",
        SubscriptionPaymentAPIView.as_view(),
        name="subscription-payment",
    ),

    path(
        "<int:payment_id>/status/",
        PaymentStatusAPIView.as_view(),
        name="payment-status",
    ),

    path(
        "<int:payment_id>/verify/",
        PaymentVerificationAPIView.as_view(),
        name="payment-verification",
    ),
]