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


def test_load_cv_seed_links_certificate_to_experience_and_education() -> None:
    """The EFZ certificate references the apprenticeship via link keys; load wires both FKs."""
    call_command("load_cv_seed")
    cert = models.Certificate.objects.get(name__startswith="Federal Apprenticeship")
    assert cert.experience is not None
    assert cert.experience.role.startswith("Apprentice")
    assert cert.education is not None
    assert cert.education.degree.startswith("Federal Apprenticeship")


def test_load_cv_seed_supports_unlinked_certificate() -> None:
    """The Cambridge English cert has no experience_key/education_key — stays unlinked."""
    call_command("load_cv_seed")
    cert = models.Certificate.objects.get(name__startswith="Cambridge")
    assert cert.experience is None
    assert cert.education is None


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
    """A custom seed without link_keys still loads experiences, educations and certs."""
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
        "experiences": [
            {
                "role": "Engineer",
                "company": "ACME",
                "start_date": "2020-01-01",
            }
        ],
        "educations": [
            {
                "degree": "BSc",
                "institution": "Uni",
                "start_date": "2017-09-01",
                "end_date": "2020-06-30",
            }
        ],
        "certificates": [
            {
                "name": "Standalone",
                "issuer": "Body",
                "issue_date": "2021-01-01",
            }
        ],
        "projects": [],
        "timeline_entries": [],
    }
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    call_command("load_cv_seed", f"--path={path}")
    person = models.Person.objects.get(slug="test-person")
    assert person.experiences.count() == 1
    assert person.educations.count() == 1
    cert = person.certificates.get()
    assert cert.experience is None
    assert cert.education is None
