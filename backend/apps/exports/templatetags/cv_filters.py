"""Template filters for CV export templates."""

from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


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


def _read(obj: Any, key: str) -> str:
    value = obj.get(key, "") if isinstance(obj, dict) else getattr(obj, key, "")
    return value if isinstance(value, str) else (str(value) if value else "")
