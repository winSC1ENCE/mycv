"""Model-level tests — str representations, ordering, and the ``full_name``
property. Exercises every model so the coverage gate stays at 100%."""

from __future__ import annotations

import datetime as dt

import pytest

from apps.cv import models

from .factories import (
    CertificateFactory,
    EducationFactory,
    ExperienceFactory,
    MediaAssetFactory,
    PersonFactory,
    ProjectFactory,
    SkillCategoryFactory,
    SkillFactory,
    SocialLinkFactory,
    TechnologyFactory,
    TimelineEntryFactory,
)

pytestmark = pytest.mark.django_db


def test_person_str_and_full_name() -> None:
    person = PersonFactory(first_name="Nicolas", last_name="Mischler")
    assert str(person) == "Nicolas Mischler"
    assert person.full_name == "Nicolas Mischler"


def test_technology_str() -> None:
    tech = TechnologyFactory(name="Django")
    assert str(tech) == "Django"


def test_skill_category_str() -> None:
    cat = SkillCategoryFactory(name="Backend")
    assert str(cat) == "Backend"


def test_skill_str_includes_category() -> None:
    cat = SkillCategoryFactory(name="Backend")
    skill = SkillFactory(name="Python", category=cat)
    assert "Python" in str(skill)
    assert "Backend" in str(skill)


def test_experience_str_and_ordering() -> None:
    person = PersonFactory()
    older = ExperienceFactory(person=person, start_date=dt.date(2020, 1, 1))
    newer = ExperienceFactory(person=person, start_date=dt.date(2024, 1, 1))
    assert list(models.Experience.objects.all()) == [newer, older]
    assert "@" in str(newer)


def test_education_str_and_ordering() -> None:
    person = PersonFactory()
    older = EducationFactory(person=person, start_date=dt.date(2015, 1, 1))
    newer = EducationFactory(person=person, start_date=dt.date(2020, 1, 1))
    assert list(models.Education.objects.all()) == [newer, older]
    assert "—" in str(newer)


def test_certificate_str_and_ordering() -> None:
    person = PersonFactory()
    older = CertificateFactory(person=person, issue_date=dt.date(2020, 6, 1))
    newer = CertificateFactory(person=person, issue_date=dt.date(2024, 6, 1))
    assert list(models.Certificate.objects.all()) == [newer, older]
    assert "(" in str(newer)


def test_project_str() -> None:
    project = ProjectFactory(name="mycv")
    assert str(project) == "mycv"


def test_social_link_str() -> None:
    link = SocialLinkFactory(url="https://example.com")
    assert "example.com" in str(link)


def test_timeline_entry_str_and_ordering() -> None:
    person = PersonFactory()
    older = TimelineEntryFactory(person=person, date=dt.date(2020, 1, 1))
    newer = TimelineEntryFactory(person=person, date=dt.date(2024, 1, 1))
    assert list(models.TimelineEntry.objects.all()) == [newer, older]
    assert "2024" in str(newer)


def test_media_asset_str() -> None:
    asset = MediaAssetFactory()
    assert asset.kind in str(asset)
