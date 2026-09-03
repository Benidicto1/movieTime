"""
URL configuration for MovieTime backend.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    # --------------------------------------------------------
    # Admin
    # --------------------------------------------------------

    path(
        "admin/",
        admin.site.urls,
    ),

    # --------------------------------------------------------
    # Movies
    # --------------------------------------------------------

    path(
        "api/v1/movies/",
        include("movies.urls"),
    ),

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    path(
        "api/v1/auth/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "api/v1/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    # --------------------------------------------------------
    # Purchases
    # --------------------------------------------------------

    path(
        "api/v1/",
        include("purchases.urls"),
    ),

    # --------------------------------------------------------
    # Downloads
    # --------------------------------------------------------

    path(
        "api/v1/downloads/",
        include("downloads.urls"),
    ),

    # --------------------------------------------------------
    # Payments
    # --------------------------------------------------------

    path(
        "api/v1/payments/",
        include("payments.urls"),
    ),

    # --------------------------------------------------------
    # Notifications
    # --------------------------------------------------------

    path(
        "api/v1/notifications/",
        include("notifications.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )