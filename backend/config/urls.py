"""Root URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.db import OperationalError, connection
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.exports.sitemaps import ProjectSitemap, StaticSitemap


def healthz(_request):  # type: ignore[no-untyped-def]
    """Liveness probe — process is up."""
    return JsonResponse({"status": "ok"})


def readyz(_request):  # type: ignore[no-untyped-def]
    """Readiness probe — process can serve traffic (DB reachable)."""
    try:
        connection.ensure_connection()
        return JsonResponse({"status": "ready", "db": "ok"})
    except OperationalError as exc:
        return JsonResponse({"status": "not-ready", "db": str(exc)}, status=503)


sitemaps = {"static": StaticSitemap, "projects": ProjectSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", healthz, name="health"),
    path("api/ready/", readyz, name="ready"),
    path("api/auth/", include("apps.accounts.urls")),
    # exports must precede the cv router so /api/cv/pdf/ wins over /api/cv/<slug>/
    path("api/", include("apps.exports.urls")),
    path("api/", include("apps.cv.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
