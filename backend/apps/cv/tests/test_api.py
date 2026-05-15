"""API tests covering every router endpoint and the nested CV detail."""

from __future__ import annotations

import pytest
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
