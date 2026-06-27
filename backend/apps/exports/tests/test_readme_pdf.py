"""Tests for the admin README PDF export endpoint."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.cv.tests.factories import AccessKeyFactory, PersonFactory, ReadmeFactory
from apps.exports.readme import render_readme_body

User = get_user_model()
pytestmark = pytest.mark.django_db

_FAKE_PDF = b"%PDF-fake"


@pytest.fixture()
def admin_client() -> APIClient:
    user = User.objects.create_user(username="admin", password="x", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _url(pk: int) -> str:
    return f"/api/admin/readmes/{pk}/pdf/"


class TestPermissionsAndValidation:
    def test_anon_forbidden(self, api_client: APIClient) -> None:
        readme = ReadmeFactory()
        resp = api_client.post(_url(readme.pk), {"lang": "en"}, format="json")
        assert resp.status_code == 403

    def test_invalid_lang_400(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory()
        resp = admin_client.post(_url(readme.pk), {"lang": "fr"}, format="json")
        assert resp.status_code == 400

    def test_svgs_must_be_list(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory()
        resp = admin_client.post(_url(readme.pk), {"svgs": "nope"}, format="json")
        assert resp.status_code == 400

    def test_invalid_doc_400(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory()
        resp = admin_client.post(_url(readme.pk), {"doc": "cover"}, format="json")
        assert resp.status_code == 400

    def test_missing_readme_404(self, admin_client: APIClient) -> None:
        resp = admin_client.post(_url(9999), {"lang": "en"}, format="json")
        assert resp.status_code == 404


class TestPdfRendering:
    def test_basic_pdf_stream(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory(name="ACME GmbH")
        with patch("apps.exports.readme._render_pdf", return_value=_FAKE_PDF):
            resp = admin_client.post(_url(readme.pk), {}, format="json")  # lang/svgs default
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/pdf"
        assert resp.content == _FAKE_PDF
        assert 'filename="acme-gmbh.pdf"' in resp["Content-Disposition"]

    def test_de_uses_german_body(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory(content="English here", content_de="Deutsch hier")
        with patch("apps.exports.readme._render_pdf", return_value=_FAKE_PDF) as render:
            admin_client.post(_url(readme.pk), {"lang": "de"}, format="json")
        html = render.call_args.args[0]
        assert "Deutsch hier" in html
        assert "English here" not in html

    def test_de_falls_back_to_english_when_empty(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory(content="Only English", content_de="")
        with patch("apps.exports.readme._render_pdf", return_value=_FAKE_PDF) as render:
            admin_client.post(_url(readme.pk), {"lang": "de"}, format="json")
        assert "Only English" in render.call_args.args[0]

    def test_mermaid_block_replaced_with_svg(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory(content="```mermaid\nflowchart TD\nA-->B\n```")
        with patch("apps.exports.readme._render_pdf", return_value=_FAKE_PDF) as render:
            admin_client.post(
                _url(readme.pk),
                {"svgs": ["<svg>DIAGRAM</svg>"]},
                format="json",
            )
        html = render.call_args.args[0]
        assert "<svg>DIAGRAM</svg>" in html
        assert "language-mermaid" not in html

    def test_mermaid_block_kept_when_no_svg(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory(content="```mermaid\nflowchart TD\nA-->B\n```")
        with patch("apps.exports.readme._render_pdf", return_value=_FAKE_PDF) as render:
            admin_client.post(_url(readme.pk), {"svgs": []}, format="json")
        assert "language-mermaid" in render.call_args.args[0]

    def test_placeholders_substituted(self, admin_client: APIClient) -> None:
        person = PersonFactory(is_published=True)
        key = AccessKeyFactory(person=person)
        readme = ReadmeFactory(
            person=person,
            access_key=key,
            content="Open {{access_url}} until {{expires_at}} — {{version}} / {{updated}}",
            version="v3.1.4",
        )
        with patch("apps.exports.readme._render_pdf", return_value=_FAKE_PDF) as render:
            admin_client.post(_url(readme.pk), {"lang": "en"}, format="json")
        html = render.call_args.args[0]
        assert "{{access_url}}" not in html
        assert f"?key={key.token}" in html
        assert "v3.1.4" in html
        # access URL renders as a clickable anchor, not bare text
        assert "<a " in html
        assert f'href="http://testserver/?key={key.token}"' in html

    def test_badges_token_renders_chips_and_name_is_not_a_heading(
        self, admin_client: APIClient
    ) -> None:
        readme = ReadmeFactory(
            name="ACME GmbH",
            version="v4.2.0",
            content="# My Manual Title\n\n{{badges}}\n\nbody",
        )
        with patch("apps.exports.readme._render_pdf", return_value=_FAKE_PDF) as render:
            admin_client.post(_url(readme.pk), {"lang": "en"}, format="json")
        html = render.call_args.args[0]
        assert "{{badges}}" not in html
        assert "rm-badge" in html
        assert "v4.2.0" in html  # version chip value
        assert "<h1>My Manual Title</h1>" in html  # author's heading is the H1
        # name is only PDF metadata (<title>), never a rendered heading/band
        assert "<h1>ACME GmbH</h1>" not in html
        assert "rm-name" not in html

    def test_base_url_override(self, admin_client: APIClient) -> None:
        person = PersonFactory(is_published=True)
        key = AccessKeyFactory(person=person)
        readme = ReadmeFactory(person=person, access_key=key, content="Open {{access_url}}")
        with patch("apps.exports.readme._render_pdf", return_value=_FAKE_PDF) as render:
            admin_client.post(
                _url(readme.pk),
                {"lang": "en", "base_url": "https://cv.example.com/"},
                format="json",
            )
        html = render.call_args.args[0]
        assert f'href="https://cv.example.com/?key={key.token}"' in html
        assert "testserver" not in html


class TestLetterPdf:
    def test_letter_renders_reference_badge_and_letter_body(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory(
            name="ACME GmbH",
            content="# README body",
            letter_reference="JOB-2026-042",
            letter_content="# Motivation\n\n{{badges}}\n\nDear team",
        )
        with patch("apps.exports.readme._render_pdf", return_value=_FAKE_PDF) as render:
            resp = admin_client.post(_url(readme.pk), {"doc": "letter"}, format="json")
        html = render.call_args.args[0]
        assert "Dear team" in html  # letter body, not the README body
        assert "README body" not in html
        assert "JOB-2026-042" in html  # reference chip value
        assert ">reference<" in html  # reference chip key label
        assert 'filename="acme-gmbh-letter.pdf"' in resp["Content-Disposition"]

    def test_letter_de_uses_german_letter_body(self, admin_client: APIClient) -> None:
        readme = ReadmeFactory(
            letter_content="English letter",
            letter_content_de="Deutscher Brief",
        )
        with patch("apps.exports.readme._render_pdf", return_value=_FAKE_PDF) as render:
            admin_client.post(_url(readme.pk), {"doc": "letter", "lang": "de"}, format="json")
        html = render.call_args.args[0]
        assert "Deutscher Brief" in html
        assert "English letter" not in html


class TestRenderReadmeBodyHelper:
    def test_no_key_blanks_access_placeholders(self) -> None:
        readme = ReadmeFactory(
            access_key=None,
            content="A {{access_url}} B {{expires_at}} C {{version}}",
            version="v9",
        )
        out = render_readme_body(readme, "en", "http://x/")
        assert out == "A  B  C v9"

    def test_letter_doc_selects_letter_content(self) -> None:
        readme = ReadmeFactory(content="readme body", letter_content="letter body")
        assert render_readme_body(readme, "en", "http://x/", doc="letter") == "letter body"
