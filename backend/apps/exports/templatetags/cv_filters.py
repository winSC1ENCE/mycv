"""Template filters for CV export templates."""

from __future__ import annotations

from typing import Any

import markdown as md
import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_ALLOWED_TAGS = {
    "p",
    "br",
    "strong",
    "em",
    "ul",
    "ol",
    "li",
    "a",
    "code",
    "h3",
    "h4",
    "blockquote",
}
_ALLOWED_ATTRS = {"a": {"href"}}

MAX_SKILL_LEVEL = 5

_LEGEND_LABELS = {
    "de": [
        "Produktiver Einsatz / Expertenniveau",
        "Regelmäßiger Einsatz",
        "Projektbezogener Einsatz",
        "Grundlagen angewendet",
        "Erste Berührungspunkte",
    ],
    "en": [
        "Production use / expert",
        "Regular use",
        "Project-based use",
        "Applied fundamentals",
        "First exposure",
    ],
}


@register.filter(name="localize")
def localize(obj: Any, lang: str) -> str:
    """Return a localized text value for the given language.

    ``obj`` may be a model instance, dict, or string. ``lang`` is "en" or "de".
    For model instances/dicts, when ``lang == "de"`` and a ``<attr>_de`` variant
    exists and is non-empty, return it; otherwise fall back to the base value.

    Usage in templates:
        {{ experience|localize_attr:"role"|localize:lang }}

    Or for direct dual-field objects passed via a helper context entry.
    """
    if isinstance(obj, str):
        return obj
    return str(obj) if obj is not None else ""


@register.simple_tag
def localized(obj: Any, field: str, lang: str) -> str:
    """Return ``obj.<field>_de`` when lang='de' and non-empty, else ``obj.<field>``.

    Works with model instances and dicts.
    """
    if obj is None:
        return ""
    base = _read(obj, field) or ""
    if lang != "de":
        return base
    de = _read(obj, f"{field}_de") or ""
    return de or base


@register.simple_tag(name="markdown")
def markdown_tag(obj: Any, field: str, lang: str) -> str:
    """Render the localized ``<field>`` value as sanitized Markdown HTML.

    Mirrors ``localized`` for de/en resolution, then converts Markdown to HTML
    and strips everything outside a tight allowlist (parity with the web app's
    markdown-it + DOMPurify pipeline).
    """
    text = localized(obj, field, lang)
    if not text:
        return ""
    html = md.markdown(text, extensions=["sane_lists", "nl2br"])
    # nh3.clean strips everything outside the allowlist, so the result is safe to mark.
    clean = nh3.clean(html, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRS)
    return mark_safe(clean)  # nosec B308 B703 # noqa: S308


@register.simple_tag
def skill_dots(level: Any) -> str:
    """Render a 1-5 proficiency level as five dots (filled = level).

    Invalid or missing levels render as zero filled dots; values above
    ``MAX_SKILL_LEVEL`` are clamped.
    """
    try:
        filled = int(level)
    except TypeError, ValueError:
        filled = 0
    filled = max(0, min(filled, MAX_SKILL_LEVEL))
    dots = "".join(
        f'<span class="dot{" dot--on" if i < filled else ""}"></span>'
        for i in range(MAX_SKILL_LEVEL)
    )
    # Markup is fully static (no user input), so it is safe to mark.
    return mark_safe(f'<span class="dots">{dots}</span>')  # nosec B308 B703 # noqa: S308


@register.simple_tag
def skill_legend(lang: str) -> list[dict[str, Any]]:
    """Return the proficiency legend rows (levels 5→1) for the given language."""
    labels = _LEGEND_LABELS.get(lang, _LEGEND_LABELS["en"])
    return [{"level": MAX_SKILL_LEVEL - i, "label": label} for i, label in enumerate(labels)]


def _read(obj: Any, key: str) -> str:
    value = obj.get(key, "") if isinstance(obj, dict) else getattr(obj, key, "")
    return value if isinstance(value, str) else (str(value) if value else "")
