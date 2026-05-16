"""Sitemap definitions for SEO."""

from __future__ import annotations

import datetime as dt
from typing import Any, cast

from django.contrib.sitemaps import Sitemap
from django.db.models import QuerySet

from apps.cv.models import Project


class StaticSitemap(Sitemap):  # type: ignore[type-arg]
    """Top-level public pages."""

    changefreq = "weekly"
    priority = 0.9

    def items(self) -> list[str]:
        return ["/"]

    def location(self, item: str) -> str:
        return item


class ProjectSitemap(Sitemap):  # type: ignore[type-arg]
    """Published project detail pages."""

    changefreq = "monthly"
    priority = 0.6

    def items(self) -> QuerySet[Project]:
        return Project.objects.filter(is_published=True)

    def location(self, obj: Any) -> str:
        return f"/projects/{obj.slug}"

    def lastmod(self, obj: Any) -> dt.datetime:
        return cast(dt.datetime, obj.updated_at)
