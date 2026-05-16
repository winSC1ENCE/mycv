"""Idempotently load the curated CV seed JSON into the database.

Usage::

    python manage.py load_cv_seed
    python manage.py load_cv_seed --path /custom/path/seed.json
    python manage.py load_cv_seed --flush
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.cv import models

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "seed.json"


class Command(BaseCommand):
    help = "Load (or reload) the curated CV seed data."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Wipe existing CV tables before loading.",
        )

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        path: Path = options["path"]
        if not path.exists():
            raise CommandError(f"Seed file not found: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))

        if options["flush"]:
            self._flush()

        person = self._upsert_person(payload["person"])
        self._upsert_social_links(person, payload.get("social_links", []))
        tech_by_slug = self._upsert_technologies(payload.get("technologies", []))
        self._upsert_skills(payload.get("skill_categories", []), tech_by_slug)
        exp_by_key = self._upsert_experiences(person, payload.get("experiences", []), tech_by_slug)
        edu_by_key = self._upsert_educations(person, payload.get("educations", []))
        self._upsert_certificates(person, payload.get("certificates", []), exp_by_key, edu_by_key)
        self._upsert_projects(person, payload.get("projects", []), tech_by_slug)
        self._upsert_timeline(person, payload.get("timeline_entries", []))

        self.stdout.write(self.style.SUCCESS(f"Seeded CV for {person.full_name}."))

    @staticmethod
    def _flush() -> None:
        for model in (
            models.TimelineEntry,
            models.SocialLink,
            models.Project,
            models.Certificate,
            models.Education,
            models.Experience,
            models.Skill,
            models.SkillCategory,
            models.Technology,
            models.MediaAsset,
            models.Person,
        ):
            model.objects.all().delete()

    @staticmethod
    def _upsert_person(data: dict[str, Any]) -> models.Person:
        person, _ = models.Person.objects.update_or_create(
            slug=data["slug"], defaults={k: v for k, v in data.items() if k != "slug"}
        )
        return person

    @staticmethod
    def _upsert_social_links(person: models.Person, entries: list[dict[str, Any]]) -> None:
        person.social_links.all().delete()
        for order, entry in enumerate(entries):
            models.SocialLink.objects.create(person=person, order=order, **entry)

    @staticmethod
    def _upsert_technologies(entries: list[dict[str, Any]]) -> dict[str, models.Technology]:
        out: dict[str, models.Technology] = {}
        for order, entry in enumerate(entries):
            tech, _ = models.Technology.objects.update_or_create(
                slug=entry["slug"],
                defaults={**{k: v for k, v in entry.items() if k != "slug"}, "order": order},
            )
            out[tech.slug] = tech
        return out

    @staticmethod
    def _upsert_skills(
        categories: list[dict[str, Any]], tech_by_slug: dict[str, models.Technology]
    ) -> None:
        for cat_order, cat in enumerate(categories):
            skills_data = cat.pop("skills", [])
            category, _ = models.SkillCategory.objects.update_or_create(
                slug=cat["slug"],
                defaults={**{k: v for k, v in cat.items() if k != "slug"}, "order": cat_order},
            )
            category.skills.all().delete()
            for skill_order, skill_data in enumerate(skills_data):
                tech_slugs = skill_data.pop("technologies", [])
                skill = models.Skill.objects.create(
                    category=category, order=skill_order, **skill_data
                )
                skill.technologies.set([tech_by_slug[s] for s in tech_slugs if s in tech_by_slug])

    @staticmethod
    def _upsert_experiences(
        person: models.Person,
        entries: list[dict[str, Any]],
        tech_by_slug: dict[str, models.Technology],
    ) -> dict[str, models.Experience]:
        person.experiences.all().delete()
        out: dict[str, models.Experience] = {}
        for order, entry in enumerate(entries):
            tech_slugs = entry.pop("technologies", [])
            link_key = entry.pop("link_key", None)
            exp = models.Experience.objects.create(person=person, order=order, **entry)
            exp.technologies.set([tech_by_slug[s] for s in tech_slugs if s in tech_by_slug])
            if link_key:
                out[link_key] = exp
        return out

    @staticmethod
    def _upsert_educations(
        person: models.Person, entries: list[dict[str, Any]]
    ) -> dict[str, models.Education]:
        person.educations.all().delete()
        out: dict[str, models.Education] = {}
        for order, entry in enumerate(entries):
            link_key = entry.pop("link_key", None)
            edu = models.Education.objects.create(person=person, order=order, **entry)
            if link_key:
                out[link_key] = edu
        return out

    @staticmethod
    def _upsert_certificates(
        person: models.Person,
        entries: list[dict[str, Any]],
        exp_by_key: dict[str, models.Experience],
        edu_by_key: dict[str, models.Education],
    ) -> None:
        person.certificates.all().delete()
        for order, entry in enumerate(entries):
            exp_key = entry.pop("experience_key", None)
            edu_key = entry.pop("education_key", None)
            models.Certificate.objects.create(
                person=person,
                order=order,
                experience=exp_by_key.get(exp_key) if exp_key else None,
                education=edu_by_key.get(edu_key) if edu_key else None,
                **entry,
            )

    @staticmethod
    def _upsert_projects(
        person: models.Person,
        entries: list[dict[str, Any]],
        tech_by_slug: dict[str, models.Technology],
    ) -> None:
        person.projects.all().delete()
        for order, entry in enumerate(entries):
            tech_slugs = entry.pop("technologies", [])
            project = models.Project.objects.create(person=person, order=order, **entry)
            project.technologies.set([tech_by_slug[s] for s in tech_slugs if s in tech_by_slug])

    @staticmethod
    def _upsert_timeline(person: models.Person, entries: list[dict[str, Any]]) -> None:
        person.timeline_entries.all().delete()
        for order, entry in enumerate(entries):
            models.TimelineEntry.objects.create(person=person, order=order, **entry)
