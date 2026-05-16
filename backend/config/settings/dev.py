"""Development settings — local Docker compose."""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True

# Dev runs the frontend on Vite ports (3000 dev, 3001 e2e); allow both for CSRF.
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

INTERNAL_IPS = ["127.0.0.1"]
