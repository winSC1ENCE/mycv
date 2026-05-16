"""Tests for authentication endpoints."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture()
def user(db):
    return User.objects.create_user(
        username="nicolas", password="s3cur3p@ss", email="n@example.com"
    )


@pytest.fixture()
def staff_user(db):
    return User.objects.create_user(
        username="admin", password="s3cur3p@ss", email="admin@example.com", is_staff=True
    )


@pytest.fixture()
def client():
    return APIClient()


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


def test_login_valid_credentials(client, user):
    resp = client.post(reverse("auth-login"), {"username": "nicolas", "password": "s3cur3p@ss"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "nicolas"
    assert data["is_staff"] is False
    assert "password" not in data


def test_login_bad_password(client, user):
    resp = client.post(reverse("auth-login"), {"username": "nicolas", "password": "wrong"})
    assert resp.status_code == 400


def test_login_unknown_user(client, db):
    resp = client.post(reverse("auth-login"), {"username": "nobody", "password": "x"})
    assert resp.status_code == 400


def test_login_sets_session(client, user):
    resp = client.post(reverse("auth-login"), {"username": "nicolas", "password": "s3cur3p@ss"})
    assert resp.status_code == 200
    # Session cookie is present after login
    assert "sessionid" in client.cookies


def test_login_staff_flag(client, staff_user):
    resp = client.post(reverse("auth-login"), {"username": "admin", "password": "s3cur3p@ss"})
    assert resp.status_code == 200
    assert resp.json()["is_staff"] is True


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


def test_logout_authenticated(client, user):
    client.force_authenticate(user=user)
    resp = client.post(reverse("auth-logout"))
    assert resp.status_code == 204


def test_logout_anonymous(client):
    resp = client.post(reverse("auth-logout"))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Me
# ---------------------------------------------------------------------------


def test_me_authenticated(client, user):
    client.force_authenticate(user=user)
    resp = client.get(reverse("auth-me"))
    assert resp.status_code == 200
    assert resp.json()["username"] == "nicolas"


def test_me_anonymous(client):
    resp = client.get(reverse("auth-me"))
    assert resp.status_code == 403
