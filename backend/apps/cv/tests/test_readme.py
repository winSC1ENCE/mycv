"""Tests for the Readme model, serializers and admin-only ViewSet."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.cv import models
from apps.cv.tests.factories import AccessKeyFactory, PersonFactory, ReadmeFactory

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture()
def admin_client() -> APIClient:
    user = User.objects.create_user(username="admin", password="x", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestReadmeModel:
    def test_str_returns_name(self) -> None:
        assert str(ReadmeFactory(name="ACME GmbH")) == "ACME GmbH"


class TestReadmePermissions:
    def test_anon_cannot_list(self, api_client: APIClient) -> None:
        resp = api_client.get("/api/admin/readmes/")
        assert resp.status_code == 403

    def test_anon_cannot_create(self, api_client: APIClient) -> None:
        resp = api_client.post("/api/admin/readmes/", {"name": "X"}, format="json")
        assert resp.status_code == 403


class TestReadmeCrud:
    def test_admin_creates_autofilling_person(self, admin_client: APIClient) -> None:
        person = PersonFactory(is_published=True)
        resp = admin_client.post(
            "/api/admin/readmes/",
            {"name": "ACME", "content": "# Hi", "version": "v2.0.0"},
            format="json",
        )
        assert resp.status_code == 201
        readme = models.Readme.objects.get(pk=resp.data["id"])
        assert readme.person == person
        assert readme.name == "ACME"

    def test_admin_creates_with_access_key(self, admin_client: APIClient) -> None:
        person = PersonFactory(is_published=True)
        key = AccessKeyFactory(person=person)
        resp = admin_client.post(
            "/api/admin/readmes/",
            {"name": "ACME", "access_key": key.pk},
            format="json",
        )
        assert resp.status_code == 201
        assert models.Readme.objects.get(pk=resp.data["id"]).access_key == key

    def test_admin_updates(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory()
        resp = admin_client.patch(
            f"/api/admin/readmes/{readme.pk}/", {"name": "Renamed"}, format="json"
        )
        assert resp.status_code == 200
        readme.refresh_from_db()
        assert readme.name == "Renamed"

    def test_admin_deletes(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory()
        resp = admin_client.delete(f"/api/admin/readmes/{readme.pk}/")
        assert resp.status_code == 204
        assert not models.Readme.objects.filter(pk=readme.pk).exists()


class TestReadmeSerializerComputed:
    def test_access_fields_empty_without_key(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory(access_key=None)
        resp = admin_client.get(f"/api/admin/readmes/{readme.pk}/")
        assert resp.data["access_url"] == ""
        assert resp.data["expires_display"] == ""

    def test_access_fields_resolved_with_key(self, admin_client: APIClient) -> None:
        person = PersonFactory(is_published=True)
        key = AccessKeyFactory(person=person)
        readme = ReadmeFactory(person=person, access_key=key)
        resp = admin_client.get(f"/api/admin/readmes/{readme.pk}/")
        assert resp.data["access_url"] == f"http://testserver/?key={key.token}"
        expected = timezone.localtime(key.expires_at).strftime("%d.%m.%Y %H:%M")
        assert resp.data["expires_display"] == expected

    def test_updated_display_present(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory()
        resp = admin_client.get(f"/api/admin/readmes/{readme.pk}/")
        expected = timezone.localtime(readme.updated_at).strftime("%d.%m.%Y")
        assert resp.data["updated_display"] == expected
