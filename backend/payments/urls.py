from django.urls import path

from .views import (
    AirtelPaymentWebhookAPIView,
    MTNPaymentWebhookAPIView,
)


urlpatterns = [
    path(
        "webhooks/mtn/",
        MTNPaymentWebhookAPIView.as_view(),
        name="mtn-payment-webhook",
    ),

    path(
        "webhooks/airtel/",
        AirtelPaymentWebhookAPIView.as_view(),
        name="airtel-payment-webhook",
    ),
]