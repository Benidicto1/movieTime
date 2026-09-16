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
    # ========================================================
    # DJANGO ADMIN
    # ========================================================

    path(
        "admin/",
        admin.site.urls,
    ),


    # ========================================================
    # MOVIES API
    # ========================================================

    path(
        "api/v1/movies/",
        include("movies.urls"),
    ),


    # ========================================================
    # JWT AUTHENTICATION
    # ========================================================

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


    # ========================================================
    # PURCHASES API
    # ========================================================

    path(
        "api/v1/",
        include("purchases.urls"),
    ),


    # ========================================================
    # DOWNLOADS API
    # ========================================================

    path(
        "api/v1/downloads/",
        include("downloads.urls"),
    ),


    # ========================================================
    # PAYMENTS API
    # ========================================================

    path(
        "api/v1/payments/",
        include("payments.urls"),
    ),


    # ========================================================
    # NOTIFICATIONS API
    # ========================================================

    path(
        "api/v1/notifications/",
        include("notifications.urls"),
    ),
]


# ============================================================
# DEVELOPMENT MEDIA FILE SERVING
# ============================================================
#
# Django serves local media files only when DEBUG=True.
#
# Production MovieTime movie files should NOT be served
# directly through Django. They should eventually use private
# object storage/CDN with signed URLs.
# ============================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )