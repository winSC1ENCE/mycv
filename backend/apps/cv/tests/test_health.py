"""Tests for health, readiness, and security headers."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from django.db import OperationalError
from rest_framework.test import APIClient


@pytest.fixture()
def client() -> APIClient:
    return APIClient()


# ---------------------------------------------------------------------------
# /api/health/  (liveness — process is up)
# ---------------------------------------------------------------------------


def test_health_returns_ok(client: APIClient) -> None:
    resp = client.get("/api/health/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /api/ready/  (readiness — DB is reachable)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_ready_returns_ok_when_db_up(client: APIClient) -> None:
    resp = client.get("/api/ready/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert data["db"] == "ok"


def test_ready_returns_503_when_db_down(client: APIClient) -> None:
    with patch(
        "django.db.connection.ensure_connection",
        side_effect=OperationalError("connection refused"),
    ):
        resp = client.get("/api/ready/")
    assert resp.status_code == 503
    data = resp.json()
    assert data["status"] == "not-ready"
    assert "connection refused" in data["db"]


# ---------------------------------------------------------------------------
# CSP header — present when CONTENT_SECURITY_POLICY is configured
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_csp_header_present_when_configured(client: APIClient) -> None:
    from django.test import override_settings

    csp_config = {"DIRECTIVES": {"default-src": ["'self'"]}}
    with override_settings(CONTENT_SECURITY_POLICY=csp_config):
        resp = client.get("/api/health/")
    assert resp.status_code == 200
    assert "Content-Security-Policy" in resp.headers


@pytest.mark.django_db
def test_csp_header_absent_when_not_configured(client: APIClient) -> None:
    from django.test import override_settings

    with override_settings(CONTENT_SECURITY_POLICY={}):
        resp = client.get("/api/health/")
    assert resp.status_code == 200
    # Empty config → no CSP header added
    assert "Content-Security-Policy" not in resp.headers
