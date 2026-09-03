"""
Django settings for config project.

MovieTime backend configuration.
"""

import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY environment variable is required."
    )


DEBUG = os.getenv(
    "DJANGO_DEBUG",
    "True",
).lower() in {
    "true",
    "1",
    "yes",
    "on",
}


ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if host.strip()
]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "django_filters",

    "movies.apps.MoviesConfig",
    "payments.apps.PaymentsConfig",
    "purchases.apps.PurchasesConfig",
    "downloads.apps.DownloadsConfig",
    "accounts.apps.AccountsConfig",
    "favorites.apps.FavoritesConfig",
    "subscriptions.apps.SubscriptionsConfig",
    "notifications.apps.NotificationsConfig",
]


AUTH_USER_MODEL = "accounts.User"


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),

    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),

    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination",
    ),

    "PAGE_SIZE": 20,
}


# ============================================================
# JWT
# ============================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=30
    ),

    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=7
    ),

    "AUTH_HEADER_TYPES": (
        "Bearer",
    ),
}


# ============================================================
# MTN MOBILE MONEY
# ============================================================

MTN_MOMO_BASE_URL = os.getenv(
    "MTN_MOMO_BASE_URL"
)

MTN_MOMO_API_USER = os.getenv(
    "MTN_MOMO_API_USER"
)

MTN_MOMO_API_KEY = os.getenv(
    "MTN_MOMO_API_KEY"
)

MTN_MOMO_SUBSCRIPTION_KEY = os.getenv(
    "MTN_MOMO_SUBSCRIPTION_KEY"
)

MTN_MOMO_TARGET_ENVIRONMENT = os.getenv(
    "MTN_MOMO_TARGET_ENVIRONMENT",
    "sandbox",
)

MTN_MOMO_CALLBACK_URL = os.getenv(
    "MTN_MOMO_CALLBACK_URL"
)


# ============================================================
# AIRTEL MONEY
# ============================================================

AIRTEL_BASE_URL = os.getenv(
    "AIRTEL_BASE_URL"
)

AIRTEL_CLIENT_ID = os.getenv(
    "AIRTEL_CLIENT_ID"
)

AIRTEL_CLIENT_SECRET = os.getenv(
    "AIRTEL_CLIENT_SECRET"
)


# ============================================================
# MOVIETIME STORAGE
# ============================================================

MOVIETIME_STORAGE = {
    "PRIVATE_BUCKET": "movietime-media",
    "PRIVATE_PREFIX": "private/movies/",
    "SIGNED_URL_EXPIRATION": 600,
}


MOVIETIME_STORAGE_BUCKET = os.getenv(
    "MOVIETIME_STORAGE_BUCKET"
)

MOVIETIME_CDN_DOMAIN = os.getenv(
    "MOVIETIME_CDN_DOMAIN"
)

MOVIETIME_SIGNED_URL_EXPIRATION = int(
    os.getenv(
        "MOVIETIME_SIGNED_URL_EXPIRATION",
        "600",
    )
)


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL / WSGI
# ============================================================

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django.DjangoTemplates"
        ),
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors.request"
                ),
                (
                    "django.contrib.auth.context_processors.auth"
                ),
                (
                    "django.contrib.messages.context_processors.messages"
                ),
            ],
        },
    },
]


# ============================================================
# DATABASE
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": (
            "django.db.backends.sqlite3"
        ),
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC / MEDIA
# ============================================================

STATIC_URL = "static/"

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# EMAIL
# ============================================================

MAILERS = {
    "default": {
        "BACKEND": (
            "django.core.mail.backends.console.EmailBackend"
        ),
    },
}