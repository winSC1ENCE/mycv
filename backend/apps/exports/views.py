"""PDF export endpoint for the CV."""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import segno
from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponse
from django.template.loader import render_to_string
from pypdf import PdfReader, PdfWriter
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.cv import models

VALID_LANGS = {"en", "de"}
CERT_KINDS: set[str] = {models.MediaAsset.Kind.IMAGE, models.MediaAsset.Kind.DOCUMENT}


@dataclass
class _CertEntry:
    """One attachment to render: a CI header plus its scan (image or PDF)."""

    kicker: str
    title: str
    subtitle: str
    dates: str
    media: models.MediaAsset


def _render_pdf(html: str, base_url: str, *, title: str, author: str) -> bytes:
    """Render HTML to PDF via WeasyPrint. Isolated for easy mocking in tests."""
    from weasyprint import HTML  # imported lazily so test envs without libs can skip

    return cast(
        bytes,
        HTML(string=html, base_url=base_url).write_pdf(
            metadata={"title": title, "author": author},
        ),
    )


def _build_qr_svg(url: str) -> str:
    qr = segno.make(url, micro=False)
    buf = io.BytesIO()
    qr.save(buf, kind="svg", scale=4, xmldecl=False, svgns=True)
    return buf.getvalue().decode("utf-8")


def _read_css(filename: str = "cv.css") -> str:
    """Load a PDF stylesheet and substitute the absolute font directory."""
    css_path = Path(settings.BASE_DIR) / "templates" / "exports" / filename
    fonts_dir = (Path(settings.BASE_DIR) / "static" / "fonts").resolve()
    return css_path.read_text(encoding="utf-8").replace("__FONTS__", str(fonts_dir))


def _localized(obj: object, field: str, lang: str) -> str:
    """Return ``obj.<field>_de`` for German (when non-empty), else ``obj.<field>``."""
    base = getattr(obj, field, "")
    if lang != "de":
        return base
    return getattr(obj, f"{field}_de", "") or base


def _assemble_pdf(parts: list[bytes], *, title: str, author: str) -> bytes:
    """Concatenate PDF byte blobs (rendered pages + raw attachments) into one PDF."""
    writer = PdfWriter()
    for data in parts:
        for page in PdfReader(io.BytesIO(data)).pages:
            writer.add_page(page)
    writer.add_metadata({"/Title": title, "/Author": author})
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


class CvPdfView(APIView):
    """``GET /api/cv/pdf/?lang=en|de`` — stream the CV PDF (staff only).

    Renders the normal-theme CV only. The admin SPA supplies ``base_url`` (the
    visitor-facing origin) since the backend's request Host is the internal proxy.
    """

    permission_classes = [IsAdminUser]

    def get(self, request: Request) -> HttpResponse:
        lang = request.query_params.get("lang", "en")
        if lang not in VALID_LANGS:
            raise ValidationError({"lang": f"Must be one of {sorted(VALID_LANGS)}."})

        person = (
            models.Person.objects.filter(is_published=True)
            .prefetch_related(
                "experiences__technologies",
                "educations",
                "certificates",
                "social_links",
            )
            .first()
        )
        if person is None:
            raise NotFound("No published CV.")

        # Only skills flagged for PDF export; drop categories left empty.
        skill_categories = [
            cat
            for cat in models.SkillCategory.objects.filter(is_published=True)
            .prefetch_related(
                Prefetch("skills", queryset=models.Skill.objects.filter(show_in_pdf=True))
            )
            .order_by("order", "id")
            if cat.skills.all()
        ]

        public_url = request.query_params.get("base_url") or request.build_absolute_uri("/")
        html = render_to_string(
            "exports/cv.html",
            {
                "person": person,
                "skill_categories": skill_categories,
                "lang": lang,
                "public_url": public_url,
                "qr_svg": _build_qr_svg(public_url),
                "css": _read_css(),
            },
        )

        pdf_bytes = _render_pdf(
            html,
            base_url=str(settings.BASE_DIR),
            title=f"{person.full_name} — CV",
            author=person.full_name,
        )

        filename = f"{person.first_name}_{person.last_name}_CV_{lang.upper()}.pdf"
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp


def _cert_entries(person: models.Person, lang: str) -> list[_CertEntry]:
    """Collect the scans attached to published Experience/Education entries.

    Experiences first, then education. Each ``media`` is an image (embedded inline,
    i.e. converted to a page) or a PDF document whose pages are appended after the header.
    """
    present = "heute" if lang == "de" else "Present"
    entries: list[_CertEntry] = []

    experiences = (
        models.Experience.objects.filter(person=person, is_published=True, media__isnull=False)
        .select_related("media")
        .order_by("order", "id")
    )
    for exp in experiences:
        media = exp.media
        if media is None or media.kind not in CERT_KINDS:
            continue
        end = exp.end_date.strftime("%Y-%m") if exp.end_date else present
        entries.append(
            _CertEntry(
                kicker="Erfahrung" if lang == "de" else "Experience",
                title=_localized(exp, "role", lang),
                subtitle=exp.company + (f" · {exp.location}" if exp.location else ""),
                dates=f"{exp.start_date.strftime('%Y-%m')} — {end}",
                media=media,
            )
        )

    educations = (
        models.Education.objects.filter(person=person, is_published=True, media__isnull=False)
        .select_related("media")
        .order_by("order", "id")
    )
    for ed in educations:
        media = ed.media
        if media is None or media.kind not in CERT_KINDS:
            continue
        end = f" — {ed.end_date.strftime('%Y')}" if ed.end_date else ""
        entries.append(
            _CertEntry(
                kicker="Ausbildung" if lang == "de" else "Education",
                title=_localized(ed, "degree", lang),
                subtitle=ed.institution + (f" · {ed.location}" if ed.location else ""),
                dates=f"{ed.start_date.strftime('%Y')}{end}",
                media=media,
            )
        )

    return entries


class CertificatesPdfView(APIView):
    """``GET /api/cv/certificates/pdf/?lang=en|de`` — bundle Experience/Education scans.

    One PDF, staff-only: a cover page, then a CI-styled header per entry with its
    certificate image embedded inline; PDF attachments are merged in after their header.
    """

    permission_classes = [IsAdminUser]

    def get(self, request: Request) -> HttpResponse:
        lang = request.query_params.get("lang", "en")
        if lang not in VALID_LANGS:
            raise ValidationError({"lang": f"Must be one of {sorted(VALID_LANGS)}."})

        person = models.Person.objects.filter(is_published=True).first()
        if person is None:
            raise NotFound("No published CV.")

        entries = _cert_entries(person, lang)
        if not entries:
            raise NotFound("No certificates to export.")

        css = _read_css("certificates.css")
        base_url = str(settings.BASE_DIR)
        title = f"{person.full_name} — Certificates"

        parts: list[bytes] = [
            _render_pdf(
                render_to_string(
                    "exports/certificates_cover.html",
                    {"person": person, "lang": lang, "count": len(entries), "css": css},
                ),
                base_url=base_url,
                title=title,
                author=person.full_name,
            )
        ]
        for entry in entries:
            media = entry.media
            parts.append(
                _render_pdf(
                    render_to_string(
                        "exports/certificates_entry.html",
                        {
                            "entry": entry,
                            "lang": lang,
                            "css": css,
                            "is_image": media.kind == models.MediaAsset.Kind.IMAGE,
                            "media_path": media.file.path,
                        },
                    ),
                    base_url=base_url,
                    title=title,
                    author=person.full_name,
                )
            )
            if media.kind == models.MediaAsset.Kind.DOCUMENT:
                parts.append(Path(media.file.path).read_bytes())

        pdf_bytes = _assemble_pdf(parts, title=title, author=person.full_name)
        filename = f"{person.first_name}_{person.last_name}_Certificates_{lang.upper()}.pdf"
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
