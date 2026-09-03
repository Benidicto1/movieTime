from django.urls import path

from .views import (
    SubscriptionPaymentAPIView,
)


urlpatterns = [

    path(
        "subscriptions/",
        SubscriptionPaymentAPIView.as_view(),
        name="subscription-payment",
    ),

]
