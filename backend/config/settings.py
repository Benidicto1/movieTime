"""
Django settings for config project.

MovieTime backend configuration.
"""

import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


# ============================================================
# BASE CONFIGURATION
# ============================================================

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
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "django_filters",

    # MovieTime applications
    "movies.apps.MoviesConfig",
    "payments.apps.PaymentsConfig",
    "purchases.apps.PurchasesConfig",
    "downloads.apps.DownloadsConfig",
    "accounts.apps.AccountsConfig",
    "favorites.apps.FavoritesConfig",
    "subscriptions.apps.SubscriptionsConfig",
    "notifications.apps.NotificationsConfig",
]


# ============================================================
# CUSTOM USER MODEL
# ============================================================

AUTH_USER_MODEL = "accounts.User"


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    # --------------------------------------------------------
    # Permissions
    # --------------------------------------------------------

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),

    # --------------------------------------------------------
    # Filtering / Searching / Ordering
    # --------------------------------------------------------

    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination",
    ),

    "PAGE_SIZE": 20,

    # --------------------------------------------------------
    # Global Rate Limiting
    # --------------------------------------------------------

    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),

    "DEFAULT_THROTTLE_RATES": {
        # General API protection
        "anon": "30/minute",
        "user": "120/minute",

        # Sensitive MovieTime operations
        "authentication": "5/minute",
        "payment": "10/minute",
        "purchase": "10/minute",
        "download": "20/minute",
        "stream": "30/minute",
        "payment_status": "30/minute",
    },
}


# ============================================================
# JWT CONFIGURATION
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
# CACHE / RATE-LIMIT STORAGE
# ============================================================

CACHE_BACKEND = os.getenv(
    "DJANGO_CACHE_BACKEND",
    "local",
).lower()


if CACHE_BACKEND == "redis":

    REDIS_URL = os.getenv(
        "REDIS_URL"
    )

    if not REDIS_URL:
        raise ImproperlyConfigured(
            "REDIS_URL is required when "
            "DJANGO_CACHE_BACKEND=redis."
        )

    CACHES = {
        "default": {
            "BACKEND": (
                "django_redis.cache.RedisCache"
            ),
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": (
                    "django_redis.client.DefaultClient"
                ),
            },
        }
    }

else:

    CACHES = {
        "default": {
            "BACKEND": (
                "django.core.cache.backends.locmem."
                "LocMemCache"
            ),
            "LOCATION": "movietime-rate-limit",
        }
    }


# ============================================================
# ABUSE PREVENTION
# ============================================================

MOVIETIME_ABUSE_PREVENTION = {
    "ENABLE_DUPLICATE_OPERATION_CHECKS": True,
    "ENABLE_PAYMENT_REPLAY_PROTECTION": True,
    "ENABLE_OBJECT_OWNERSHIP_CHECKS": True,
    "ENABLE_STATE_VALIDATION": True,
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
            "django.template.backends.django."
            "DjangoTemplates"
        ),

        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
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
# STATIC FILES
# ============================================================

STATIC_URL = "static/"


# ============================================================
# MEDIA FILES
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# EMAIL
# ============================================================

MAILERS = {
    "default": {
        "BACKEND": (
            "django.core.mail.backends.console."
            "EmailBackend"
        ),
    },
}


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"