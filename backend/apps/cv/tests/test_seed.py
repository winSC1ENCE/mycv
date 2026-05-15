"""Tests for the ``load_cv_seed`` management command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.cv import models

pytestmark = pytest.mark.django_db


def test_load_cv_seed_creates_records() -> None:
    call_command("load_cv_seed")
    person = models.Person.objects.get(slug="nicolas-mischler")
    assert person.experiences.exists()
    assert person.educations.exists()
    assert person.projects.exists()
    assert person.social_links.exists()
    assert person.timeline_entries.exists()
    assert models.Technology.objects.filter(slug="python").exists()
    assert models.SkillCategory.objects.filter(slug="backend").exists()


def test_load_cv_seed_is_idempotent() -> None:
    call_command("load_cv_seed")
    call_command("load_cv_seed")
    assert models.Person.objects.filter(slug="nicolas-mischler").count() == 1


def test_load_cv_seed_flush() -> None:
    call_command("load_cv_seed")
    call_command("load_cv_seed", "--flush")
    assert models.Person.objects.count() == 1


def test_load_cv_seed_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    with pytest.raises(CommandError):
        call_command("load_cv_seed", f"--path={missing}")


def test_load_cv_seed_custom_path(tmp_path: Path) -> None:
    payload = {
        "person": {
            "slug": "test-person",
            "first_name": "Test",
            "last_name": "Person",
            "title": "Engineer",
            "email": "t@example.com",
        },
        "social_links": [],
        "technologies": [],
        "skill_categories": [],
        "experiences": [],
        "educations": [],
        "certificates": [],
        "projects": [],
        "timeline_entries": [],
    }
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    call_command("load_cv_seed", f"--path={path}")
    assert models.Person.objects.filter(slug="test-person").exists()
