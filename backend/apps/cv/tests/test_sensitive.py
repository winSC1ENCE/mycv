"""Tests for sensitive field redaction and AccessKey unlock flow."""

from __future__ import annotations

import datetime as dt

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.cv import models

from .factories import PersonFactory


@pytest.fixture()
def person(db: None) -> models.Person:
    return PersonFactory(
        email="nicolas@example.com",
        phone="+41 79 123 45 67",
        address="Musterstrasse 1, 3000 Bern",
        zivilstand="ledig",
        date_of_birth=dt.date(1990, 5, 15),
    )


@pytest.fixture()
def valid_key(person: models.Person) -> models.AccessKey:
    return models.AccessKey.objects.create(
        person=person,
        label="test",
        expires_at=timezone.now() + dt.timedelta(hours=1),
    )


@pytest.fixture()
def expired_key(person: models.Person) -> models.AccessKey:
    return models.AccessKey.objects.create(
        person=person,
        label="expired",
        expires_at=timezone.now() - dt.timedelta(hours=1),
    )


@pytest.fixture()
def revoked_key(person: models.Person) -> models.AccessKey:
    return models.AccessKey.objects.create(
        person=person,
        label="revoked",
        expires_at=timezone.now() + dt.timedelta(hours=1),
        is_active=False,
    )


SENSITIVE_FIELDS = ("email", "phone", "address", "zivilstand", "date_of_birth")


@pytest.mark.django_db
class TestAccessKeyModel:
    def test_str_with_label(self, valid_key: models.AccessKey) -> None:
        valid_key.label = "recruiter"
        assert "recruiter" in str(valid_key)

    def test_str_without_label_uses_token_prefix(self, valid_key: models.AccessKey) -> None:
        valid_key.label = ""
        assert valid_key.token[:8] in str(valid_key)

    def test_is_valid_true_for_active_unexpired(self, valid_key: models.AccessKey) -> None:
        assert valid_key.is_valid is True

    def test_is_valid_false_when_expired(self, expired_key: models.AccessKey) -> None:
        assert expired_key.is_valid is False

    def test_is_valid_false_when_revoked(self, revoked_key: models.AccessKey) -> None:
        assert revoked_key.is_valid is False


@pytest.mark.django_db
class TestAnonymousRedaction:
    def test_sensitive_fields_redacted(self, person: models.Person) -> None:
        data = APIClient().get("/api/cv/").json()
        assert data["access_granted"] is False
        assert data["email"] == "***@***.***"
        assert data["phone"] == "••• ••• ••••"
        assert data["address"] == "••• ••• ••• •••"
        assert data["zivilstand"] == "•••••"
        assert data["date_of_birth"] is None

    def test_real_values_not_in_response(self, person: models.Person) -> None:
        body = str(APIClient().get("/api/cv/").content)
        assert "nicolas@example.com" not in body
        assert "+41 79 123 45 67" not in body
        assert "Musterstrasse" not in body
        assert "ledig" not in body


@pytest.mark.django_db
class TestInvalidKeyRedaction:
    def test_bogus_key_still_redacted(self, person: models.Person) -> None:
        data = APIClient().get("/api/cv/?key=notarealtoken").json()
        assert data["access_granted"] is False
        assert data["email"] == "***@***.***"

    def test_expired_key_still_redacted(
        self, person: models.Person, expired_key: models.AccessKey
    ) -> None:
        data = APIClient().get(f"/api/cv/?key={expired_key.token}").json()
        assert data["access_granted"] is False
        assert data["email"] == "***@***.***"

    def test_revoked_key_still_redacted(
        self, person: models.Person, revoked_key: models.AccessKey
    ) -> None:
        data = APIClient().get(f"/api/cv/?key={revoked_key.token}").json()
        assert data["access_granted"] is False
        assert data["email"] == "***@***.***"


@pytest.mark.django_db
class TestValidKeyUnlock:
    def test_valid_key_returns_real_values(
        self, person: models.Person, valid_key: models.AccessKey
    ) -> None:
        data = APIClient().get(f"/api/cv/?key={valid_key.token}").json()
        assert data["access_granted"] is True
        assert data["email"] == "nicolas@example.com"
        assert data["phone"] == "+41 79 123 45 67"
        assert data["address"] == "Musterstrasse 1, 3000 Bern"
        assert data["zivilstand"] == "ledig"
        assert data["date_of_birth"] == "1990-05-15"


@pytest.mark.django_db
class TestStaffAccess:
    def test_staff_user_always_sees_real_values(
        self, person: models.Person, django_user_model: type
    ) -> None:
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        data = client.get("/api/cv/").json()
        assert data["access_granted"] is True
        assert data["email"] == "nicolas@example.com"
        assert data["phone"] == "+41 79 123 45 67"
