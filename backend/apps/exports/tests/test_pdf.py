"""Tests for the PDF export endpoint."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from apps.cv.tests.factories import (
    CertificateFactory,
    EducationFactory,
    ExperienceFactory,
    PersonFactory,
    ProjectFactory,
    SkillCategoryFactory,
    SkillFactory,
    SocialLinkFactory,
    TechnologyFactory,
)

pytestmark = pytest.mark.django_db


@pytest.fixture()
def _populated_person():
    person = PersonFactory()
    tech = TechnologyFactory(slug="python", name="Python")
    cat = SkillCategoryFactory(slug="backend", name="Backend")
    skill = SkillFactory(category=cat)
    skill.technologies.add(tech)
    exp = ExperienceFactory(person=person)
    exp.technologies.add(tech)
    EducationFactory(person=person)
    CertificateFactory(person=person)
    ProjectFactory(person=person)
    SocialLinkFactory(person=person)
    return person


def test_pdf_returns_pdf_with_published_person(api_client: APIClient, _populated_person) -> None:
    resp = api_client.get("/api/cv/pdf/?lang=en&theme=normal")
    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"
    assert "Content-Disposition" in resp
    assert "_CV.pdf" in resp["Content-Disposition"]


def test_pdf_filename_uses_person_name(api_client: APIClient, _populated_person) -> None:
    resp = api_client.get("/api/cv/pdf/")
    assert _populated_person.first_name in resp["Content-Disposition"]
    assert _populated_person.last_name in resp["Content-Disposition"]


def test_pdf_defaults_to_en_normal(api_client: APIClient, _populated_person) -> None:
    resp = api_client.get("/api/cv/pdf/")
    assert resp.status_code == 200


@pytest.mark.parametrize(
    "lang,theme",
    [
        ("en", "normal"),
        ("de", "normal"),
        ("en", "dog"),
        ("de", "dog"),
    ],
)
def test_pdf_all_lang_theme_combos(
    api_client: APIClient, _populated_person, lang: str, theme: str
) -> None:
    resp = api_client.get(f"/api/cv/pdf/?lang={lang}&theme={theme}")
    assert resp.status_code == 200
    assert resp.content[:4] == b"%PDF"


def test_pdf_invalid_lang_returns_400(api_client: APIClient) -> None:
    resp = api_client.get("/api/cv/pdf/?lang=fr")
    assert resp.status_code == 400


def test_pdf_invalid_theme_returns_400(api_client: APIClient) -> None:
    resp = api_client.get("/api/cv/pdf/?theme=neon")
    assert resp.status_code == 400


def test_pdf_returns_404_when_no_published_person(api_client: APIClient) -> None:
    resp = api_client.get("/api/cv/pdf/?lang=en&theme=normal")
    assert resp.status_code == 404


def test_pdf_skips_unpublished_person(api_client: APIClient) -> None:
    PersonFactory(is_published=False)
    resp = api_client.get("/api/cv/pdf/?lang=en&theme=normal")
    assert resp.status_code == 404


def test_render_pdf_wrapper_called(api_client: APIClient, _populated_person) -> None:
    """The WeasyPrint wrapper is invoked with proper metadata."""
    with patch("apps.exports.views._render_pdf", return_value=b"%PDF-fake") as mock_render:
        api_client.get("/api/cv/pdf/?lang=en&theme=normal")
        mock_render.assert_called_once()
        kwargs = mock_render.call_args.kwargs
        assert "title" in kwargs
        assert "author" in kwargs
        assert _populated_person.full_name in kwargs["title"]
