"""Test settings — fast in-memory SQLite, no throttling, axes disabled."""

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["*"]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/hour", "user": "1000/hour", "login": "5/min"},
}

AXES_ENABLED = False

CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
