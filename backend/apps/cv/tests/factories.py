"""factory_boy factories for CV models."""

from __future__ import annotations

import datetime as dt

import factory
from factory.django import DjangoModelFactory

from apps.cv import models


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = models.Person

    slug = factory.Sequence(lambda n: f"person-{n}")
    first_name = "Nicolas"
    last_name = "Mischler"
    title = "Data Engineer"
    email = factory.LazyAttribute(lambda obj: f"{obj.slug}@example.com")
    location = "Bern, Switzerland"
    summary = "Engineer."


class TechnologyFactory(DjangoModelFactory):
    class Meta:
        model = models.Technology

    name = factory.Sequence(lambda n: f"Tech-{n}")
    slug = factory.Sequence(lambda n: f"tech-{n}")
    category = "Language"


class SkillCategoryFactory(DjangoModelFactory):
    class Meta:
        model = models.SkillCategory

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class SkillFactory(DjangoModelFactory):
    class Meta:
        model = models.Skill

    name = factory.Sequence(lambda n: f"Skill {n}")
    level = 4
    category = factory.SubFactory(SkillCategoryFactory)


class ExperienceFactory(DjangoModelFactory):
    class Meta:
        model = models.Experience

    person = factory.SubFactory(PersonFactory)
    role = "Data Engineer"
    company = "ACME"
    start_date = dt.date(2023, 1, 1)
    end_date = None
    description = "Did things."


class EducationFactory(DjangoModelFactory):
    class Meta:
        model = models.Education

    person = factory.SubFactory(PersonFactory)
    degree = "BSc Computer Science"
    institution = "ETH"
    start_date = dt.date(2018, 9, 1)
    end_date = dt.date(2021, 6, 30)


class CertificateFactory(DjangoModelFactory):
    class Meta:
        model = models.Certificate

    person = factory.SubFactory(PersonFactory)
    name = factory.Sequence(lambda n: f"Cert {n}")
    issuer = "Authority"
    issue_date = dt.date(2024, 1, 1)


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = models.Project

    person = factory.SubFactory(PersonFactory)
    name = factory.Sequence(lambda n: f"Project {n}")
    slug = factory.Sequence(lambda n: f"project-{n}")
    summary = "Summary."


class SocialLinkFactory(DjangoModelFactory):
    class Meta:
        model = models.SocialLink

    person = factory.SubFactory(PersonFactory)
    platform = models.SocialLink.Platform.GITHUB
    url = "https://github.com/example"


class TimelineEntryFactory(DjangoModelFactory):
    class Meta:
        model = models.TimelineEntry

    person = factory.SubFactory(PersonFactory)
    date = dt.date(2024, 6, 1)
    kind = models.TimelineEntry.Kind.MILESTONE
    title = "Milestone"


class MediaAssetFactory(DjangoModelFactory):
    class Meta:
        model = models.MediaAsset

    file = factory.django.FileField(filename="example.png")
    alt_text = "Example"
    kind = models.MediaAsset.Kind.IMAGE
