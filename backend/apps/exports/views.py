"""PDF export endpoint for the CV."""

from __future__ import annotations

import io
from pathlib import Path
from typing import cast

import segno
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.cv import models

VALID_LANGS = {"en", "de"}
VALID_THEMES = {"normal", "dog"}


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


def _read_css() -> str:
    """Load the PDF stylesheet and substitute the absolute font directory."""
    css_path = Path(settings.BASE_DIR) / "templates" / "exports" / "cv.css"
    fonts_dir = (Path(settings.BASE_DIR) / "static" / "fonts").resolve()
    return css_path.read_text(encoding="utf-8").replace("__FONTS__", str(fonts_dir))


class CvPdfView(APIView):
    """``GET /api/cv/pdf/?lang=en|de&theme=normal|dog`` — stream a CV PDF."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> HttpResponse:
        lang = request.query_params.get("lang", "en")
        theme = request.query_params.get("theme", "normal")
        if lang not in VALID_LANGS:
            raise ValidationError({"lang": f"Must be one of {sorted(VALID_LANGS)}."})
        if theme not in VALID_THEMES:
            raise ValidationError({"theme": f"Must be one of {sorted(VALID_THEMES)}."})

        person = (
            models.Person.objects.filter(is_published=True)
            .prefetch_related(
                "experiences__technologies",
                "educations",
                "certificates",
                "projects",
                "social_links",
            )
            .first()
        )
        if person is None:
            raise NotFound("No published CV.")

        skill_categories = list(
            models.SkillCategory.objects.filter(is_published=True)
            .prefetch_related("skills")
            .order_by("order", "id")
        )

        public_url = request.build_absolute_uri("/")
        html = render_to_string(
            "exports/cv.html",
            {
                "person": person,
                "skill_categories": skill_categories,
                "lang": lang,
                "theme": theme,
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

        filename = f"{person.first_name}_{person.last_name}_CV.pdf"
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
