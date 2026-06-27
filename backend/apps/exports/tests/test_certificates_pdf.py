"""Tests for the certificates PDF export (Experience/Education attachments)."""

from __future__ import annotations

import datetime as dt
import io

import pytest
from django.contrib.auth import get_user_model
from PIL import Image
from pypdf import PdfReader, PdfWriter
from rest_framework.test import APIClient

from apps.cv import models
from apps.cv.tests.factories import (
    EducationFactory,
    ExperienceFactory,
    MediaAssetFactory,
    PersonFactory,
)

User = get_user_model()
pytestmark = pytest.mark.django_db

URL = "/api/cv/certificates/pdf/"


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), (14, 116, 144)).save(buf, "PNG")
    return buf.getvalue()


def _pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _image_media(**kw):
    return MediaAssetFactory(
        kind=models.MediaAsset.Kind.IMAGE, file__filename="cert.png", file__data=_png(), **kw
    )


def _doc_media(**kw):
    return MediaAssetFactory(
        kind=models.MediaAsset.Kind.DOCUMENT, file__filename="cert.pdf", file__data=_pdf(), **kw
    )


@pytest.fixture()
def admin_client() -> APIClient:
    user = User.objects.create_user(username="admin", password="x", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture()
def _person_with_certs(settings, tmp_path):
    """One person whose Experience/Education entries exercise every branch."""
    settings.MEDIA_ROOT = str(tmp_path)
    person = PersonFactory()
    # Experience: image, ongoing (Present), with a German role + a location.
    ExperienceFactory(
        person=person,
        role="Engineer",
        role_de="Ingenieur",
        location="Bern",
        end_date=None,
        media=_image_media(),
        order=0,
    )
    # Experience: image, finished (date range), no location.
    ExperienceFactory(
        person=person, location="", end_date=dt.date(2022, 12, 31), media=_image_media(), order=1
    )
    # Experience: video attachment → skipped.
    ExperienceFactory(
        person=person,
        media=MediaAssetFactory(kind=models.MediaAsset.Kind.VIDEO),
        order=2,
    )
    # Education: PDF document, with end date + location → pages appended after header.
    EducationFactory(
        person=person, location="Zürich", end_date=dt.date(2021, 6, 30), media=_doc_media(), order=0
    )
    # Education: image, no end date.
    EducationFactory(person=person, location="", end_date=None, media=_image_media(), order=1)
    # Education: video → skipped.
    EducationFactory(
        person=person, media=MediaAssetFactory(kind=models.MediaAsset.Kind.VIDEO), order=2
    )
    return person


class TestPermissionsAndValidation:
    def test_anon_forbidden(self, api_client: APIClient) -> None:
        assert api_client.get(URL).status_code == 403

    def test_non_staff_forbidden(self, api_client: APIClient) -> None:
        api_client.force_authenticate(user=User.objects.create_user(username="u", password="x"))
        assert api_client.get(URL).status_code == 403

    def test_invalid_lang_400(self, admin_client: APIClient) -> None:
        assert admin_client.get(f"{URL}?lang=fr").status_code == 400

    def test_no_published_person_404(self, admin_client: APIClient) -> None:
        assert admin_client.get(URL).status_code == 404

    def test_no_certificates_404(self, admin_client: APIClient) -> None:
        PersonFactory()  # published person but no media-bearing entries
        assert admin_client.get(URL).status_code == 404


class TestRendering:
    def test_merged_pdf_en(self, admin_client: APIClient, _person_with_certs) -> None:
        resp = admin_client.get(f"{URL}?lang=en")
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/pdf"
        assert resp.content[:4] == b"%PDF"
        assert "_Certificates_EN.pdf" in resp["Content-Disposition"]
        # cover + 4 entry headers (2 exp img, 1 edu doc, 1 edu img) + 1 appended doc page.
        pages = len(PdfReader(io.BytesIO(resp.content)).pages)
        assert pages >= 6

    def test_merged_pdf_de(self, admin_client: APIClient, _person_with_certs) -> None:
        resp = admin_client.get(f"{URL}?lang=de")
        assert resp.status_code == 200
        assert "_Certificates_DE.pdf" in resp["Content-Disposition"]
