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
    exp_media = MediaAssetFactory()
    exp = ExperienceFactory(person=person, media=exp_media)
    exp.technologies.add(tech)
    edu_media = MediaAssetFactory()
    EducationFactory(person=person, media=edu_media)
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
    exp_payload = body["experiences"][0]
    assert exp_payload["media"] is not None
    assert exp_payload["media"]["kind"] == "image"
    assert exp_payload["media"]["url"] == ""  # gated behind AccessKey for anonymous
    edu_payload = body["educations"][0]
    assert edu_payload["media"] is not None
    assert edu_payload["media"]["url"] == ""  # gated behind AccessKey for anonymous


def test_cv_list_404_when_no_published_person(api_client: APIClient) -> None:
    resp = api_client.get("/api/cv/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_cv_detail_by_slug(api_client: APIClient) -> None:
    person = PersonFactory(slug="me")
    resp = api_client.get(f"/api/cv/{person.slug}/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["slug"] == "me"


def test_cv_exposes_active_funny_theme_with_default(api_client: APIClient) -> None:
    PersonFactory()
    body = api_client.get("/api/cv/").json()
    assert body["active_funny_theme"] == "dog"


def test_admin_can_update_active_funny_theme(admin_client: APIClient) -> None:
    person = PersonFactory(slug="me")
    resp = admin_client.patch(
        f"/api/cv/{person.slug}/", {"active_funny_theme": "virus"}, format="json"
    )
    assert resp.status_code == status.HTTP_200_OK
    person.refresh_from_db()
    assert person.active_funny_theme == "virus"


def test_admin_cannot_set_invalid_funny_theme(admin_client: APIClient) -> None:
    person = PersonFactory(slug="me")
    resp = admin_client.patch(
        f"/api/cv/{person.slug}/", {"active_funny_theme": "cats"}, format="json"
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "path,factory",
    [
        ("/api/experiences/", ExperienceFactory),
        ("/api/educations/", EducationFactory),
        ("/api/certificates/", CertificateFactory),
        ("/api/projects/", ProjectFactory),
        ("/api/technologies/", TechnologyFactory),
        ("/api/skill-categories/", SkillCategoryFactory),
        ("/api/skills/", SkillFactory),
        ("/api/social-links/", SocialLinkFactory),
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


def test_skill_category_detail_by_slug(api_client: APIClient) -> None:
    cat = SkillCategoryFactory(slug="backend")
    resp = api_client.get(f"/api/skill-categories/{cat.slug}/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["slug"] == "backend"


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
        "/api/skills/",
        "/api/social-links/",
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
# Slug-keyed viewsets must also resolve detail routes by numeric id, so the
# admin SPA (which keys mutations by id) can edit/delete them.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path,factory",
    [
        ("/api/technologies/", TechnologyFactory),
        ("/api/projects/", ProjectFactory),
        ("/api/skill-categories/", SkillCategoryFactory),
    ],
)
def test_admin_can_update_slug_keyed_entity_by_id(
    admin_client: APIClient, path: str, factory: type
) -> None:
    obj = factory()
    resp = admin_client.patch(f"{path}{obj.pk}/", {"is_published": False}, format="json")
    assert resp.status_code == status.HTTP_200_OK
    obj.refresh_from_db()
    assert obj.is_published is False


@pytest.mark.parametrize(
    "path,factory,model",
    [
        ("/api/technologies/", TechnologyFactory, models.Technology),
        ("/api/projects/", ProjectFactory, models.Project),
        ("/api/skill-categories/", SkillCategoryFactory, models.SkillCategory),
    ],
)
def test_admin_can_delete_slug_keyed_entity_by_id(
    admin_client: APIClient, path: str, factory: type, model: type
) -> None:
    obj = factory()
    resp = admin_client.delete(f"{path}{obj.pk}/")
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert not model.objects.filter(pk=obj.pk).exists()


def test_admin_create_project_applies_media_order(admin_client: APIClient) -> None:
    person = PersonFactory()
    # ``a`` already sits at its target index 0 (exercises the skip branch).
    a, b, c = MediaAssetFactory(order=0), MediaAssetFactory(order=5), MediaAssetFactory(order=5)
    resp = admin_client.post(
        "/api/projects/",
        {"person": person.pk, "name": "Gallery", "slug": "gallery", "media": [a.pk, b.pk, c.pk]},
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    detail = admin_client.get("/api/projects/gallery/")
    assert [m["id"] for m in detail.json()["media"]] == [a.pk, b.pk, c.pk]
    b.refresh_from_db()
    assert b.order == 1


def test_admin_reorder_project_media_persists(admin_client: APIClient) -> None:
    project = ProjectFactory()
    a, b, c = (MediaAssetFactory(order=i) for i in range(3))
    project.media.set([a, b, c])

    new_order = [c.pk, a.pk, b.pk]
    resp = admin_client.patch(f"/api/projects/{project.pk}/", {"media": new_order}, format="json")
    assert resp.status_code == status.HTTP_200_OK

    detail = admin_client.get(f"/api/projects/{project.slug}/")
    assert [m["id"] for m in detail.json()["media"]] == new_order


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
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_admin_cv_list_includes_unpublished(admin_client: APIClient) -> None:
    PersonFactory(is_published=False)
    resp = admin_client.get("/api/cv/")
    assert resp.status_code == status.HTTP_200_OK


def test_certificate_exposes_experience_and_education_fks(api_client: APIClient) -> None:
    person = PersonFactory()
    exp = ExperienceFactory(person=person)
    edu = EducationFactory(person=person)
    CertificateFactory(person=person, experience=exp, education=edu)
    CertificateFactory(person=person)  # unlinked
    resp = api_client.get("/api/cv/")
    body = resp.json()
    certs = sorted(body["certificates"], key=lambda c: c["experience"] or 0)
    assert certs[0]["experience"] is None
    assert certs[0]["education"] is None
    assert certs[1]["experience"] == exp.pk
    assert certs[1]["education"] == edu.pk


def test_certificate_fk_becomes_null_when_experience_deleted() -> None:
    person = PersonFactory()
    exp = ExperienceFactory(person=person)
    cert = CertificateFactory(person=person, experience=exp)
    exp.delete()
    cert.refresh_from_db()
    assert cert.experience is None
    assert models.Certificate.objects.filter(pk=cert.pk).exists()


def test_admin_can_create_certificate_with_links(admin_client: APIClient) -> None:
    person = PersonFactory()
    exp = ExperienceFactory(person=person)
    edu = EducationFactory(person=person)
    resp = admin_client.post(
        "/api/certificates/",
        {
            "name": "Linked Cert",
            "issuer": "Authority",
            "issue_date": "2024-01-01",
            "experience": exp.pk,
            "education": edu.pk,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    cert = models.Certificate.objects.get(name="Linked Cert")
    assert cert.experience_id == exp.pk
    assert cert.education_id == edu.pk


@pytest.mark.parametrize(
    "path,factory",
    [
        ("/api/experiences/", ExperienceFactory),
        ("/api/educations/", EducationFactory),
        ("/api/certificates/", CertificateFactory),
        ("/api/projects/", ProjectFactory),
        ("/api/technologies/", TechnologyFactory),
        ("/api/skill-categories/", SkillCategoryFactory),
        ("/api/skills/", SkillFactory),
        ("/api/social-links/", SocialLinkFactory),
        ("/api/timeline/", TimelineEntryFactory),
    ],
)
def test_admin_sees_unpublished_entities(admin_client: APIClient, path: str, factory: type) -> None:
    factory(is_published=False)
    resp = admin_client.get(path)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["count"] == 1


def test_admin_can_create_skill(admin_client: APIClient) -> None:
    cat = SkillCategoryFactory()
    tech = TechnologyFactory(slug="python")
    resp = admin_client.post(
        "/api/skills/",
        {
            "name": "Python",
            "name_de": "Python",
            "category": cat.pk,
            "level": 5,
            "technologies": [tech.pk],
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    skill = models.Skill.objects.get(name="Python")
    assert skill.category_id == cat.pk
    assert skill.level == 5
    assert list(skill.technologies.values_list("slug", flat=True)) == ["python"]


def test_admin_can_update_skill(admin_client: APIClient) -> None:
    skill = SkillFactory(level=3)
    resp = admin_client.patch(
        f"/api/skills/{skill.pk}/",
        {"level": 5},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    skill.refresh_from_db()
    assert skill.level == 5


def test_admin_can_delete_skill(admin_client: APIClient) -> None:
    skill = SkillFactory()
    resp = admin_client.delete(f"/api/skills/{skill.pk}/")
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert not models.Skill.objects.filter(pk=skill.pk).exists()


def test_admin_can_toggle_skill_show_in_pdf(admin_client: APIClient) -> None:
    skill = SkillFactory()
    assert skill.show_in_pdf is True  # model default
    resp = admin_client.patch(
        f"/api/skills/{skill.pk}/",
        {"show_in_pdf": False},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    skill.refresh_from_db()
    assert skill.show_in_pdf is False


def test_skill_read_payload_includes_show_in_pdf(api_client: APIClient) -> None:
    skill = SkillFactory(show_in_pdf=False)
    resp = api_client.get(f"/api/skills/{skill.pk}/")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["show_in_pdf"] is False


def test_admin_can_create_social_link_with_person_autofill(admin_client: APIClient) -> None:
    person = PersonFactory(is_published=True)
    resp = admin_client.post(
        "/api/social-links/",
        {"platform": "github", "label": "GitHub", "url": "https://github.com/x"},
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    link = models.SocialLink.objects.get(url="https://github.com/x")
    assert link.person_id == person.pk


def test_admin_can_update_social_link(admin_client: APIClient) -> None:
    link = SocialLinkFactory(url="https://old.example/x")
    resp = admin_client.patch(
        f"/api/social-links/{link.pk}/",
        {"url": "https://new.example/x"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    link.refresh_from_db()
    assert link.url == "https://new.example/x"


def test_admin_can_delete_social_link(admin_client: APIClient) -> None:
    link = SocialLinkFactory()
    resp = admin_client.delete(f"/api/social-links/{link.pk}/")
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert not models.SocialLink.objects.filter(pk=link.pk).exists()
