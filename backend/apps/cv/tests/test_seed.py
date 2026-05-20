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
    assert models.SkillCategory.objects.exists()
    assert models.Skill.objects.exists()


def test_load_cv_seed_links_certificate_to_experience_and_education(tmp_path: Path) -> None:
    """A cert with experience_key + education_key gets both FKs wired by the loader."""
    payload = {
        "person": {
            "slug": "linked-person",
            "first_name": "L",
            "last_name": "P",
            "title": "Engineer",
            "email": "lp@example.com",
        },
        "social_links": [],
        "technologies": [],
        "skill_categories": [],
        "experiences": [
            {"link_key": "job", "role": "Engineer", "company": "ACME", "start_date": "2020-01-01"}
        ],
        "educations": [
            {
                "link_key": "school",
                "degree": "BSc",
                "institution": "Uni",
                "start_date": "2017-09-01",
                "end_date": "2020-06-30",
            }
        ],
        "certificates": [
            {
                "experience_key": "job",
                "education_key": "school",
                "name": "Linked Cert",
                "issuer": "Body",
                "issue_date": "2020-12-01",
            }
        ],
        "projects": [],
        "timeline_entries": [],
    }
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    call_command("load_cv_seed", f"--path={path}")
    cert = models.Certificate.objects.get(name="Linked Cert")
    assert cert.experience is not None
    assert cert.experience.role == "Engineer"
    assert cert.education is not None
    assert cert.education.degree == "BSc"


def test_load_cv_seed_supports_unlinked_certificate() -> None:
    """Certificates without experience_key / education_key stay unlinked."""
    call_command("load_cv_seed")
    unlinked = models.Certificate.objects.filter(experience__isnull=True, education__isnull=True)
    assert unlinked.exists()


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
