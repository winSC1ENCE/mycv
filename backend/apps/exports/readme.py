"""Admin-only PDF export for per-application README documents.

Mermaid diagrams can only be rendered by a browser (JavaScript), and WeasyPrint
runs no JS — so the admin SPA renders each ``mermaid`` fenced block to SVG
client-side and POSTs the SVG strings here. We convert the Markdown body to
sanitized HTML, splice the pre-rendered SVGs back in (in order), and hand the
result to WeasyPrint.

The WeasyPrint/file-IO helpers (:func:`_render_pdf`, :func:`_read_css`) live in
``views.py`` (which depends on the native WeasyPrint lib); this module imports
them so its own logic stays unit-testable.
"""

from __future__ import annotations

import re

import markdown as md
import nh3
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.cv import models

from .views import _read_css, _render_pdf

VALID_LANGS = {"en", "de"}

# Wider allowlist than the inline CV markdown: README documents are full pages
# (headings, tables, code blocks, diagrams), not short rich-text snippets.
_ALLOWED_TAGS = {
    "p",
    "br",
    "hr",
    "strong",
    "em",
    "ul",
    "ol",
    "li",
    "a",
    "code",
    "pre",
    "span",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
}
_ALLOWED_ATTRS = {"a": {"href"}, "code": {"class"}, "pre": {"class"}, "span": {"class"}}

_MARKDOWN_EXTENSIONS = ["sane_lists", "fenced_code", "tables", "nl2br"]

# python-markdown's fenced_code renders ```mermaid as
# <pre><code class="language-mermaid">…</code></pre>; match it after sanitizing.
_MERMAID_BLOCK = re.compile(
    r'<pre><code[^>]*class="[^"]*language-mermaid[^"]*"[^>]*>.*?</code></pre>',
    re.DOTALL,
)


def _placeholder_context(readme: models.Readme, public_url: str) -> dict[str, str]:
    """Resolve the ``{{token}}`` substitution map for a README.

    Mirrors ``ReadmeSerializer``'s computed fields so the live preview and the
    exported PDF render identical values.
    """
    key = readme.access_key
    return {
        "{{access_url}}": f"{public_url}?key={key.token}" if key else "",
        "{{expires_at}}": (
            timezone.localtime(key.expires_at).strftime("%d.%m.%Y %H:%M") if key else ""
        ),
        "{{version}}": readme.version,
        "{{updated}}": timezone.localtime(readme.updated_at).strftime("%d.%m.%Y"),
    }


def render_readme_body(readme: models.Readme, lang: str, public_url: str) -> str:
    """Return the localized body with ``{{placeholders}}`` substituted."""
    text = readme.content_de if (lang == "de" and readme.content_de) else readme.content
    for token, value in _placeholder_context(readme, public_url).items():
        text = text.replace(token, value)
    return text


def _inject_mermaid(html: str, svgs: list[str]) -> str:
    """Replace each ``language-mermaid`` code block with the matching SVG, in order."""
    svg_iter = iter(svgs)

    def replace(match: re.Match[str]) -> str:
        try:
            return next(svg_iter)
        except StopIteration:
            return match.group(0)

    return _MERMAID_BLOCK.sub(replace, html)


class ReadmePdfView(APIView):
    """``POST /api/admin/readmes/<pk>/pdf/`` — stream a rendered README PDF.

    Body: ``{"lang": "en"|"de", "svgs": ["<svg…>", …]}`` where ``svgs`` are the
    client-rendered Mermaid diagrams, ordered by appearance in the document.
    """

    permission_classes = [IsAdminUser]

    def post(self, request: Request, pk: int) -> HttpResponse:
        lang = request.data.get("lang", "en")
        if lang not in VALID_LANGS:
            raise ValidationError({"lang": f"Must be one of {sorted(VALID_LANGS)}."})
        svgs = request.data.get("svgs", [])
        if not isinstance(svgs, list):
            raise ValidationError({"svgs": "Must be a list of SVG strings."})

        readme = get_object_or_404(
            models.Readme.objects.select_related("access_key", "person"), pk=pk
        )

        public_url = request.build_absolute_uri("/")
        ctx = _placeholder_context(readme, public_url)
        body = render_readme_body(readme, lang, public_url)
        raw_html = md.markdown(body, extensions=_MARKDOWN_EXTENSIONS)
        clean = nh3.clean(raw_html, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRS)
        clean = _inject_mermaid(clean, [str(svg) for svg in svgs])

        html = render_to_string(
            "exports/readme.html",
            {
                "name": readme.name,
                "version": readme.version,
                "updated": ctx["{{updated}}"],
                "body": mark_safe(clean),  # nosec B308 B703 # noqa: S308
                "css": _read_css("readme.css"),
                "lang": lang,
            },
        )

        pdf_bytes = _render_pdf(
            html,
            base_url=str(settings.BASE_DIR),
            title=f"{readme.name} — README",
            author=readme.person.full_name,
        )

        filename = f"{slugify(readme.name) or 'readme'}.pdf"
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
