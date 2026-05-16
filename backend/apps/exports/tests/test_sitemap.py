"""Tests for sitemap.xml and robots.txt."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.cv.tests.factories import ProjectFactory

pytestmark = pytest.mark.django_db


def test_sitemap_xml_includes_home(api_client: APIClient) -> None:
    resp = api_client.get("/sitemap.xml")
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "<loc>" in body
    # Static section provides the home URL
    assert body.count("<loc>") >= 1


def test_sitemap_includes_published_projects(api_client: APIClient) -> None:
    ProjectFactory(slug="alpha", is_published=True)
    ProjectFactory(slug="beta", is_published=True)
    resp = api_client.get("/sitemap.xml")
    body = resp.content.decode()
    assert "/projects/alpha" in body
    assert "/projects/beta" in body


def test_sitemap_excludes_unpublished_projects(api_client: APIClient) -> None:
    ProjectFactory(slug="hidden", is_published=False)
    resp = api_client.get("/sitemap.xml")
    body = resp.content.decode()
    assert "/projects/hidden" not in body


def test_robots_txt_served(api_client: APIClient) -> None:
    resp = api_client.get("/robots.txt")
    assert resp.status_code == 200
    assert resp["Content-Type"].startswith("text/plain")
    body = resp.content.decode()
    assert "User-agent: *" in body
    assert "Sitemap:" in body
