"""Unit tests for cv_filters template tags."""

from __future__ import annotations

from apps.exports.templatetags.cv_filters import _read, localize, localized


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
