"""Tests for sensitive field redaction and AccessKey unlock flow."""

from __future__ import annotations

import datetime as dt

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.cv import models

from .factories import CertificateFactory, ExperienceFactory, MediaAssetFactory, PersonFactory


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
    def test_staff_user_sees_redacted_by_default(
        self, person: models.Person, django_user_model: type
    ) -> None:
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        data = client.get("/api/cv/").json()
        assert data["access_granted"] is False
        assert data["email"] == "***@***.***"

    def test_staff_user_with_valid_key_sees_real_values(
        self,
        person: models.Person,
        valid_key: models.AccessKey,
        django_user_model: type,
    ) -> None:
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        data = client.get(f"/api/cv/?key={valid_key.token}").json()
        assert data["access_granted"] is True
        assert data["email"] == "nicolas@example.com"


@pytest.mark.django_db
class TestCertificateMediaRedaction:
    def test_anonymous_certificate_media_url_blanked(self, person: models.Person) -> None:
        media = MediaAssetFactory()
        CertificateFactory(person=person, media=media, name="Cert with file")
        data = APIClient().get("/api/cv/").json()
        certs = data["certificates"]
        assert len(certs) == 1
        assert certs[0]["media"] is not None
        assert certs[0]["media"]["url"] == ""
        assert certs[0]["media"]["kind"] == "image"
        assert certs[0]["media"]["alt_text"] == "Example"

    def test_valid_key_returns_real_media_url(
        self, person: models.Person, valid_key: models.AccessKey
    ) -> None:
        media = MediaAssetFactory()
        CertificateFactory(person=person, media=media, name="Cert with file")
        data = APIClient().get(f"/api/cv/?key={valid_key.token}").json()
        certs = data["certificates"]
        assert len(certs) == 1
        assert certs[0]["media"]["url"]
        assert certs[0]["media"]["url"] != ""

    def test_certificate_without_media_stays_none(self, person: models.Person) -> None:
        CertificateFactory(person=person, media=None, name="Cert no file")
        data = APIClient().get("/api/cv/").json()
        certs = data["certificates"]
        assert len(certs) == 1
        assert certs[0]["media"] is None


@pytest.mark.django_db
class TestProjectMediaMaxSix:
    def test_create_project_with_seven_media_returns_400(
        self, person: models.Person, django_user_model: type
    ) -> None:
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        media_ids = [MediaAssetFactory().id for _ in range(7)]
        response = client.post(
            "/api/projects/",
            {
                "name": "Too many photos",
                "slug": "too-many-photos",
                "media": media_ids,
                "is_published": True,
            },
            format="json",
        )
        assert response.status_code == 400
        assert "media" in response.json()

    def test_create_project_with_six_media_succeeds(
        self, person: models.Person, django_user_model: type
    ) -> None:
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        media_ids = [MediaAssetFactory().id for _ in range(6)]
        response = client.post(
            "/api/projects/",
            {
                "name": "Six photos",
                "slug": "six-photos",
                "media": media_ids,
                "is_published": True,
            },
            format="json",
        )
        assert response.status_code == 201
        assert len(response.json()["media"]) == 6


@pytest.mark.django_db
class TestAdminCvEndpoint:
    def test_anonymous_returns_403(self, person: models.Person) -> None:
        response = APIClient().get("/api/admin/cv/")
        assert response.status_code in (401, 403)

    def test_non_staff_user_returns_403(
        self, person: models.Person, django_user_model: type
    ) -> None:
        regular = django_user_model.objects.create_user(username="regular", password="pass")
        client = APIClient()
        client.force_authenticate(user=regular)
        response = client.get("/api/admin/cv/")
        assert response.status_code == 403

    def test_staff_user_sees_unredacted_data(
        self, person: models.Person, django_user_model: type
    ) -> None:
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        response = client.get("/api/admin/cv/")
        assert response.status_code == 200
        data = response.json()
        assert data["access_granted"] is True
        assert data["email"] == "nicolas@example.com"
        assert data["phone"] == "+41 79 123 45 67"
        assert data["address"] == "Musterstrasse 1, 3000 Bern"
        assert data["zivilstand"] == "ledig"
        assert data["date_of_birth"] == "1990-05-15"

    def test_staff_user_with_no_person_returns_404(self, django_user_model: type) -> None:
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        response = client.get("/api/admin/cv/")
        assert response.status_code == 404

    def test_staff_user_sees_real_certificate_media_url(
        self, person: models.Person, django_user_model: type
    ) -> None:
        media = MediaAssetFactory()
        CertificateFactory(person=person, media=media, name="Cert")
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        response = client.get("/api/admin/cv/")
        assert response.status_code == 200
        certs = response.json()["certificates"]
        assert len(certs) == 1
        assert certs[0]["media"]["url"]
        assert certs[0]["media"]["url"] != ""


@pytest.mark.django_db
class TestCertificateViewsetMediaRedaction:
    def test_anonymous_list_blanks_media_url(self, person: models.Person) -> None:
        media = MediaAssetFactory()
        CertificateFactory(person=person, media=media, name="Cert", is_published=True)
        results = APIClient().get("/api/certificates/").json()["results"]
        assert len(results) == 1
        assert results[0]["media"] is not None
        assert results[0]["media"]["url"] == ""

    def test_anonymous_retrieve_blanks_media_url(self, person: models.Person) -> None:
        media = MediaAssetFactory()
        cert = CertificateFactory(person=person, media=media, name="Cert", is_published=True)
        data = APIClient().get(f"/api/certificates/{cert.id}/").json()
        assert data["media"] is not None
        assert data["media"]["url"] == ""

    def test_valid_key_returns_real_media_url(
        self, person: models.Person, valid_key: models.AccessKey
    ) -> None:
        media = MediaAssetFactory()
        cert = CertificateFactory(person=person, media=media, name="Cert", is_published=True)
        data = APIClient().get(f"/api/certificates/{cert.id}/?key={valid_key.token}").json()
        assert data["media"]["url"]
        assert data["media"]["url"] != ""

    def test_staff_sees_real_media_url(
        self, person: models.Person, django_user_model: type
    ) -> None:
        media = MediaAssetFactory()
        cert = CertificateFactory(person=person, media=media, name="Cert", is_published=True)
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        data = client.get(f"/api/certificates/{cert.id}/").json()
        assert data["media"]["url"]
        assert data["media"]["url"] != ""


@pytest.mark.django_db
class TestExperienceMediaRedaction:
    def test_cv_endpoint_blanks_experience_media_for_anonymous(
        self, person: models.Person
    ) -> None:
        media = MediaAssetFactory()
        ExperienceFactory(person=person, media=media, is_published=True)
        data = APIClient().get("/api/cv/").json()
        experiences = data["experiences"]
        assert len(experiences) == 1
        assert experiences[0]["media"] is not None
        assert experiences[0]["media"]["url"] == ""

    def test_anonymous_list_blanks_media_url(self, person: models.Person) -> None:
        media = MediaAssetFactory()
        ExperienceFactory(person=person, media=media, is_published=True)
        results = APIClient().get("/api/experiences/").json()["results"]
        assert len(results) == 1
        assert results[0]["media"] is not None
        assert results[0]["media"]["url"] == ""

    def test_anonymous_retrieve_blanks_media_url(self, person: models.Person) -> None:
        media = MediaAssetFactory()
        exp = ExperienceFactory(person=person, media=media, is_published=True)
        data = APIClient().get(f"/api/experiences/{exp.id}/").json()
        assert data["media"] is not None
        assert data["media"]["url"] == ""

    def test_valid_key_returns_real_media_url(
        self, person: models.Person, valid_key: models.AccessKey
    ) -> None:
        media = MediaAssetFactory()
        exp = ExperienceFactory(person=person, media=media, is_published=True)
        data = APIClient().get(f"/api/experiences/{exp.id}/?key={valid_key.token}").json()
        assert data["media"]["url"]
        assert data["media"]["url"] != ""

    def test_staff_sees_real_media_url(
        self, person: models.Person, django_user_model: type
    ) -> None:
        media = MediaAssetFactory()
        exp = ExperienceFactory(person=person, media=media, is_published=True)
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        data = client.get(f"/api/experiences/{exp.id}/").json()
        assert data["media"]["url"]
        assert data["media"]["url"] != ""


@pytest.mark.django_db
class TestMediaAssetViewsetGating:
    def test_anonymous_list_returns_403(self, person: models.Person) -> None:
        MediaAssetFactory()
        response = APIClient().get("/api/media-assets/")
        assert response.status_code in (401, 403)

    def test_staff_list_returns_200(self, person: models.Person, django_user_model: type) -> None:
        MediaAssetFactory()
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        response = client.get("/api/media-assets/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestAccessKeyWriteSerializer:
    def test_create_response_returns_token(
        self, person: models.Person, django_user_model: type
    ) -> None:
        staff = django_user_model.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user=staff)
        response = client.post(
            "/api/access-keys/",
            {
                "person": person.id,
                "label": "recruiter",
                "expires_at": (timezone.now() + dt.timedelta(hours=1)).isoformat(),
                "is_active": True,
            },
            format="json",
        )
        assert response.status_code == 201
        body = response.json()
        assert isinstance(body.get("token"), str)
        assert len(body["token"]) > 10
