"""API tests covering every router endpoint and the nested CV detail."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from apps.cv import models

from .factories import (
    CertificateFactory,
    EducationFactory,
    ExperienceFactory,
    MediaAssetFactory,
    PersonFactory,
    ProjectFactory,
    SkillCategoryFactory,
    SkillFactory,
    SocialLinkFactory,
    TechnologyFactory,
    TimelineEntryFactory,
)

User = get_user_model()

pytestmark = pytest.mark.django_db


def _populated_person() -> models.Person:
    person = PersonFactory()
    tech = TechnologyFactory(slug="python", name="Python")
    cat = SkillCategoryFactory(slug="backend", name="Backend")
    skill = SkillFactory(category=cat)
    skill.technologies.add(tech)
    exp = ExperienceFactory(person=person)
    exp.technologies.add(tech)
    EducationFactory(person=person)
    media = MediaAssetFactory()
    CertificateFactory(person=person, media=media)
    project = ProjectFactory(person=person)
    project.technologies.add(tech)
    project.media.add(media)
    SocialLinkFactory(person=person)
    TimelineEntryFactory(person=person)
    return person


def test_cv_list_returns_primary_person(api_client: APIClient) -> None:
    person = _populated_person()
    resp = api_client.get("/api/cv/")
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["slug"] == person.slug
    assert body["full_name"] == person.full_name
    assert len(body["experiences"]) == 1
    assert len(body["educations"]) == 1
    assert len(body["certificates"]) == 1
    assert len(body["projects"]) == 1
    assert len(body["social_links"]) == 1
    assert len(body["timeline_entries"]) == 1
    assert len(body["skill_categories"]) == 1
    assert body["skill_categories"][0]["skills"][0]["technologies"][0]["slug"] == "python"


def test_cv_list_404_when_no_published_person(api_client: APIClient) -> None:
    resp = api_client.get("/api/cv/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_cv_detail_by_slug(api_client: APIClient) -> None:
    person = PersonFactory(slug="me")
    resp = api_client.get(f"/api/cv/{person.slug}/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["slug"] == "me"


@pytest.mark.parametrize(
    "path,factory",
    [
        ("/api/experiences/", ExperienceFactory),
        ("/api/educations/", EducationFactory),
        ("/api/certificates/", CertificateFactory),
        ("/api/projects/", ProjectFactory),
        ("/api/technologies/", TechnologyFactory),
        ("/api/skill-categories/", SkillCategoryFactory),
        ("/api/timeline/", TimelineEntryFactory),
    ],
)
def test_list_endpoints_return_published_only(
    api_client: APIClient, path: str, factory: type
) -> None:
    factory()
    factory(is_published=False)
    resp = api_client.get(path)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["count"] == 1


def test_project_detail_by_slug(api_client: APIClient) -> None:
    project = ProjectFactory(slug="mycv")
    resp = api_client.get(f"/api/projects/{project.slug}/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["slug"] == "mycv"


def test_technology_detail_by_slug(api_client: APIClient) -> None:
    tech = TechnologyFactory(slug="rust")
    resp = api_client.get(f"/api/technologies/{tech.slug}/")
    assert resp.status_code == status.HTTP_200_OK


def test_health_endpoint(api_client: APIClient) -> None:
    resp = api_client.get("/api/health/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {"status": "ok"}


def test_openapi_schema(api_client: APIClient) -> None:
    resp = api_client.get("/api/schema/")
    assert resp.status_code == status.HTTP_200_OK
    assert b"openapi" in resp.content


# ---------------------------------------------------------------------------
# Permission tests — anonymous cannot write, admin can
# ---------------------------------------------------------------------------


@pytest.fixture()
def admin_client(db):
    user = User.objects.create_user(username="admin", password="x", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.parametrize(
    "path",
    [
        "/api/experiences/",
        "/api/educations/",
        "/api/certificates/",
        "/api/projects/",
        "/api/technologies/",
        "/api/timeline/",
    ],
)
def test_anon_cannot_post(api_client: APIClient, path: str) -> None:
    resp = api_client.post(path, {}, format="json")
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_create_experience(admin_client: APIClient) -> None:
    person = PersonFactory()
    resp = admin_client.post(
        "/api/experiences/",
        {
            "person": person.pk,
            "role": "Engineer",
            "company": "ACME",
            "start_date": "2023-01-01",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert models.Experience.objects.filter(role="Engineer").exists()


def test_admin_create_experience_autofills_person_when_omitted(
    admin_client: APIClient,
) -> None:
    """The admin form omits the FK; the server auto-fills from the first published person."""
    person = PersonFactory(is_published=True)
    resp = admin_client.post(
        "/api/experiences/",
        {"role": "Engineer", "company": "ACME", "start_date": "2023-01-01"},
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    exp = models.Experience.objects.get(role="Engineer")
    assert exp.person_id == person.pk


def test_admin_can_update_experience(admin_client: APIClient) -> None:
    person = PersonFactory()
    exp = ExperienceFactory(person=person, role="Old Role")
    resp = admin_client.patch(
        f"/api/experiences/{exp.pk}/",
        {"role": "New Role"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    exp.refresh_from_db()
    assert exp.role == "New Role"


def test_admin_can_delete_experience(admin_client: APIClient) -> None:
    person = PersonFactory()
    exp = ExperienceFactory(person=person)
    resp = admin_client.delete(f"/api/experiences/{exp.pk}/")
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert not models.Experience.objects.filter(pk=exp.pk).exists()


# ---------------------------------------------------------------------------
# Media asset upload
# ---------------------------------------------------------------------------


def _make_png() -> SimpleUploadedFile:
    # Minimal 1x1 PNG (67 bytes)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
        b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x11\x00\x01\xbc1\x14"
        b"I\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return SimpleUploadedFile("test.png", png_bytes, content_type="image/png")


def test_admin_can_upload_media_asset(admin_client: APIClient) -> None:
    resp = admin_client.post(
        "/api/media-assets/",
        {"file": _make_png(), "alt_text": "Test image", "kind": "image"},
        format="multipart",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "id" in data


def test_anon_cannot_upload_media_asset(api_client: APIClient) -> None:
    resp = api_client.post(
        "/api/media-assets/",
        {"file": _make_png(), "alt_text": "Test image"},
        format="multipart",
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_admin_sees_unpublished_media_assets(admin_client: APIClient) -> None:
    MediaAssetFactory(is_published=False)
    resp = admin_client.get("/api/media-assets/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["count"] == 1


def test_anon_cannot_see_unpublished_media_assets(api_client: APIClient) -> None:
    MediaAssetFactory(is_published=False)
    resp = api_client.get("/api/media-assets/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["count"] == 0


def test_admin_cv_list_includes_unpublished(admin_client: APIClient) -> None:
    PersonFactory(is_published=False)
    resp = admin_client.get("/api/cv/")
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "path,factory",
    [
        ("/api/experiences/", ExperienceFactory),
        ("/api/educations/", EducationFactory),
        ("/api/certificates/", CertificateFactory),
        ("/api/projects/", ProjectFactory),
        ("/api/technologies/", TechnologyFactory),
        ("/api/skill-categories/", SkillCategoryFactory),
        ("/api/timeline/", TimelineEntryFactory),
    ],
)
def test_admin_sees_unpublished_entities(
    admin_client: APIClient, path: str, factory: type
) -> None:
    factory(is_published=False)
    resp = admin_client.get(path)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["count"] == 1
