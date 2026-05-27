"""Unit tests for cv_filters template tags."""

from __future__ import annotations

from apps.exports.templatetags.cv_filters import _read, localize, localized, markdown_tag


class FakeObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_localize_passthrough_string():
    assert localize("hello", "en") == "hello"


def test_localize_none():
    assert localize(None, "en") == ""


def test_localize_other_type():
    assert localize(42, "en") == "42"


def test_localized_en_returns_base_field():
    obj = FakeObj(title="Engineer", title_de="Ingenieur")
    assert localized(obj, "title", "en") == "Engineer"


def test_localized_de_returns_de_field_when_present():
    obj = FakeObj(title="Engineer", title_de="Ingenieur")
    assert localized(obj, "title", "de") == "Ingenieur"


def test_localized_de_falls_back_when_de_empty():
    obj = FakeObj(title="Engineer", title_de="")
    assert localized(obj, "title", "de") == "Engineer"


def test_localized_none_obj_returns_empty():
    assert localized(None, "title", "en") == ""


def test_localized_from_dict():
    obj = {"title": "Engineer", "title_de": "Ingenieur"}
    assert localized(obj, "title", "de") == "Ingenieur"


def test_localized_missing_field_returns_empty():
    obj = FakeObj(title="Engineer")
    assert localized(obj, "missing", "en") == ""


def test_read_dict_returns_string():
    assert _read({"a": "x"}, "a") == "x"


def test_read_attr_returns_string():
    assert _read(FakeObj(a="x"), "a") == "x"


def test_read_missing_returns_empty():
    assert _read(FakeObj(), "a") == ""


def test_read_non_string_value_coerced():
    assert _read(FakeObj(a=5), "a") == "5"


def test_markdown_renders_bold_and_list():
    obj = FakeObj(description="**Bold**\n\n- one\n- two", description_de="")
    html = markdown_tag(obj, "description", "en")
    assert "<strong>Bold</strong>" in html
    assert "<ul>" in html
    assert "<li>one</li>" in html


def test_markdown_uses_de_variant():
    obj = FakeObj(description="**Hi**", description_de="**Hallo**")
    assert "<strong>Hallo</strong>" in markdown_tag(obj, "description", "de")


def test_markdown_empty_returns_empty():
    assert markdown_tag(FakeObj(description=""), "description", "en") == ""


def test_markdown_strips_dangerous_html():
    obj = FakeObj(description="ok <script>alert(1)</script>", description_de="")
    html = markdown_tag(obj, "description", "en")
    assert "<script>" not in html
    assert "alert(1)" not in html


def test_markdown_adds_rel_to_links():
    obj = FakeObj(description="[x](https://example.com)", description_de="")
    html = markdown_tag(obj, "description", "en")
    assert 'href="https://example.com"' in html
    assert 'rel="noopener noreferrer"' in html
