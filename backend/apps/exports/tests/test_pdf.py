"""Tests for the CV PDF export endpoint (staff-only, normal theme, de/en)."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.cv.tests.factories import (
    CertificateFactory,
    EducationFactory,
    ExperienceFactory,
    PersonFactory,
    SkillCategoryFactory,
    SkillFactory,
    SocialLinkFactory,
    TechnologyFactory,
)

User = get_user_model()
pytestmark = pytest.mark.django_db

_FAKE_PDF = b"%PDF-fake"


@pytest.fixture()
def admin_client() -> APIClient:
    user = User.objects.create_user(username="admin", password="x", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture()
def _populated_person():
    person = PersonFactory()
    tech = TechnologyFactory(slug="python", name="Python")
    cat = SkillCategoryFactory(slug="backend", name="Backend")
    skill = SkillFactory(category=cat)
    skill.technologies.add(tech)
    SkillFactory(category=cat, level=5)
    SkillFactory(category=cat, level=1)
    exp = ExperienceFactory(person=person)
    exp.technologies.add(tech)
    EducationFactory(person=person)
    CertificateFactory(person=person)
    SocialLinkFactory(person=person)
    return person


class TestPermissions:
    def test_anon_forbidden(self, api_client: APIClient, _populated_person) -> None:
        resp = api_client.get("/api/cv/pdf/?lang=en")
        assert resp.status_code == 403

    def test_non_staff_forbidden(self, api_client: APIClient, _populated_person) -> None:
        user = User.objects.create_user(username="plain", password="x")
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/cv/pdf/?lang=en")
        assert resp.status_code == 403


class TestPdfRendering:
    def test_returns_pdf_with_published_person(
        self, admin_client: APIClient, _populated_person
    ) -> None:
        resp = admin_client.get("/api/cv/pdf/?lang=en")
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/pdf"
        assert resp.content[:4] == b"%PDF"
        assert 'filename="' in resp["Content-Disposition"]
        assert "_CV_EN.pdf" in resp["Content-Disposition"]

    def test_filename_uses_person_name(self, admin_client: APIClient, _populated_person) -> None:
        resp = admin_client.get("/api/cv/pdf/?lang=de")
        assert _populated_person.first_name in resp["Content-Disposition"]
        assert _populated_person.last_name in resp["Content-Disposition"]
        assert "_CV_DE.pdf" in resp["Content-Disposition"]

    def test_defaults_to_en(self, admin_client: APIClient, _populated_person) -> None:
        resp = admin_client.get("/api/cv/pdf/")
        assert resp.status_code == 200
        assert "_CV_EN.pdf" in resp["Content-Disposition"]

    def test_invalid_lang_returns_400(self, admin_client: APIClient, _populated_person) -> None:
        resp = admin_client.get("/api/cv/pdf/?lang=fr")
        assert resp.status_code == 400

    def test_returns_404_when_no_published_person(self, admin_client: APIClient) -> None:
        resp = admin_client.get("/api/cv/pdf/?lang=en")
        assert resp.status_code == 404

    def test_skips_unpublished_person(self, admin_client: APIClient) -> None:
        PersonFactory(is_published=False)
        resp = admin_client.get("/api/cv/pdf/?lang=en")
        assert resp.status_code == 404


class TestRenderWrapper:
    def test_render_pdf_wrapper_called_with_metadata(
        self, admin_client: APIClient, _populated_person
    ) -> None:
        with patch("apps.exports.views._render_pdf", return_value=_FAKE_PDF) as mock_render:
            admin_client.get("/api/cv/pdf/?lang=en")
        mock_render.assert_called_once()
        kwargs = mock_render.call_args.kwargs
        assert _populated_person.full_name in kwargs["title"]
        assert kwargs["author"] == _populated_person.full_name

    def test_base_url_param_flows_into_html(
        self, admin_client: APIClient, _populated_person
    ) -> None:
        base_url = "https://cv.example.test/"
        with patch("apps.exports.views._render_pdf", return_value=_FAKE_PDF) as mock_render:
            resp = admin_client.get(f"/api/cv/pdf/?lang=en&base_url={base_url}")
        assert resp.status_code == 200
        html = mock_render.call_args.args[0]
        assert base_url in html  # rendered in the sidebar footer / online-version block


class TestShowInPdf:
    def test_hidden_skill_excluded_from_html(
        self, admin_client: APIClient, _populated_person
    ) -> None:
        cat = SkillCategoryFactory(slug="pdf-mixed", name="Mixed")
        SkillFactory(category=cat, name="Visible skill", show_in_pdf=True)
        SkillFactory(category=cat, name="Hidden skill", show_in_pdf=False)
        with patch("apps.exports.views._render_pdf", return_value=_FAKE_PDF) as mock_render:
            resp = admin_client.get("/api/cv/pdf/?lang=en")
        assert resp.status_code == 200
        html = mock_render.call_args.args[0]
        assert "Visible skill" in html
        assert "Hidden skill" not in html

    def test_category_with_only_hidden_skills_dropped(
        self, admin_client: APIClient, _populated_person
    ) -> None:
        cat = SkillCategoryFactory(slug="pdf-hidden", name="All hidden category")
        SkillFactory(category=cat, name="Invisible", show_in_pdf=False)
        with patch("apps.exports.views._render_pdf", return_value=_FAKE_PDF) as mock_render:
            resp = admin_client.get("/api/cv/pdf/?lang=en")
        assert resp.status_code == 200
        html = mock_render.call_args.args[0]
        assert "All hidden category" not in html
