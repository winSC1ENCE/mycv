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
from django.utils.html import escape
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
VALID_DOCS = {"readme", "letter"}

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
        # Angle-bracket autolink so Python-markdown emits a clickable <a> (it does
        # not linkify bare URLs the way the preview's markdown-it does). Valid both
        # bare and inside `[label](<…>)`.
        "{{access_url}}": f"<{public_url}?key={key.token}>" if key else "",
        "{{expires_at}}": (
            timezone.localtime(key.expires_at).strftime("%d.%m.%Y %H:%M") if key else ""
        ),
        "{{version}}": readme.version,
        "{{updated}}": timezone.localtime(readme.updated_at).strftime("%d.%m.%Y"),
    }


def render_readme_body(
    readme: models.Readme, lang: str, public_url: str, *, doc: str = "readme"
) -> str:
    """Return the localized body (README or letter) with ``{{placeholders}}`` substituted."""
    if doc == "letter":
        text = (
            readme.letter_content_de
            if (lang == "de" and readme.letter_content_de)
            else readme.letter_content
        )
    else:
        text = readme.content_de if (lang == "de" and readme.content_de) else readme.content
    for token, value in _placeholder_context(readme, public_url).items():
        text = text.replace(token, value)
    return text


def _badges_html(first_key: str, first_val: str, updated: str) -> str:
    """Build the two badge chips injected at the ``{{badges}}`` token.

    The first chip is document-specific (``version`` for a README, ``reference``
    for a letter); the second is always the updated date.
    """
    return (
        '<span class="rm-badges">'
        '<span class="rm-badge">'
        f'<span class="rm-badge__key">{escape(first_key)}</span>'
        f'<span class="rm-badge__val">{escape(first_val)}</span></span>'
        '<span class="rm-badge rm-badge--muted">'
        '<span class="rm-badge__key">updated</span>'
        f'<span class="rm-badge__val">{escape(updated)}</span></span>'
        "</span>"
    )


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

    Body: ``{"lang": "en"|"de", "doc": "readme"|"letter", "svgs": [...],
    "base_url": "https://…/"}`` — ``doc`` selects the README or the motivation
    letter, ``svgs`` are the client-rendered Mermaid diagrams (ordered by
    appearance), and ``base_url`` is the visitor-facing origin for the access link.
    """

    permission_classes = [IsAdminUser]

    def post(self, request: Request, pk: int) -> HttpResponse:
        lang = request.data.get("lang", "en")
        if lang not in VALID_LANGS:
            raise ValidationError({"lang": f"Must be one of {sorted(VALID_LANGS)}."})
        doc = request.data.get("doc", "readme")
        if doc not in VALID_DOCS:
            raise ValidationError({"doc": f"Must be one of {sorted(VALID_DOCS)}."})
        svgs = request.data.get("svgs", [])
        if not isinstance(svgs, list):
            raise ValidationError({"svgs": "Must be a list of SVG strings."})

        readme = get_object_or_404(
            models.Readme.objects.select_related("access_key", "person"), pk=pk
        )

        # Prefer the client's public origin: behind the dev proxy the request Host
        # is the internal "backend:8000", not what the visitor's browser sees.
        base_url = request.data.get("base_url")
        if not (isinstance(base_url, str) and base_url.startswith(("http://", "https://"))):
            base_url = request.build_absolute_uri("/")
        public_url = base_url
        ctx = _placeholder_context(readme, public_url)
        body = render_readme_body(readme, lang, public_url, doc=doc)
        raw_html = md.markdown(body, extensions=_MARKDOWN_EXTENSIONS)
        clean = nh3.clean(raw_html, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRS)
        clean = _inject_mermaid(clean, [str(svg) for svg in svgs])
        if doc == "letter":
            badges = _badges_html("reference", readme.letter_reference, ctx["{{updated}}"])
        else:
            badges = _badges_html("version", readme.version, ctx["{{updated}}"])
        clean = clean.replace("{{badges}}", badges)

        html = render_to_string(
            "exports/readme.html",
            {
                "name": readme.name,
                "body": mark_safe(clean),  # nosec B308 B703 # noqa: S308
                "css": _read_css("readme.css"),
                "lang": lang,
            },
        )

        label = "Motivation Letter" if doc == "letter" else "README"
        pdf_bytes = _render_pdf(
            html,
            base_url=str(settings.BASE_DIR),
            title=f"{readme.name} — {label}",
            author=readme.person.full_name,
        )

        slug = slugify(readme.name) or "readme"
        filename = f"{slug}-letter.pdf" if doc == "letter" else f"{slug}.pdf"
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
