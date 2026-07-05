"""CV domain models.

Conventions enforced via the :class:`Orderable` abstract base:
- ``order`` for manual sort, ``is_published`` for visibility,
  and ``created_at``/``updated_at`` timestamps.
- All foreign keys use ``PROTECT`` to prevent accidental cascading deletes.
- Translatable text fields are duplicated as ``<field>`` (English, canonical)
  and ``<field>_de`` (German) for the MVP locale strategy described in the
  implementation plan. The API exposes both, and the frontend picks one.
"""

from __future__ import annotations

import secrets

from django.db import models
from django.utils import timezone


def _generate_access_token() -> str:
    return secrets.token_urlsafe(24)


class Orderable(models.Model):
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class MediaAsset(Orderable):
    class Kind(models.TextChoices):
        IMAGE = "image", "Image"
        DOCUMENT = "document", "Document"
        VIDEO = "video", "Video"

    file = models.FileField(upload_to="uploads/%Y/%m/")
    alt_text = models.CharField(max_length=255, blank=True)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.IMAGE)

    def __str__(self) -> str:
        return f"{self.kind}: {self.file.name}"


class Technology(Orderable):
    name = models.CharField(max_length=80, unique=True, db_index=True)
    slug = models.SlugField(max_length=80, unique=True, db_index=True)
    category = models.CharField(max_length=64, blank=True)

    class Meta(Orderable.Meta):
        verbose_name_plural = "technologies"

    def __str__(self) -> str:
        return self.name


class Person(Orderable):
    class FunnyTheme(models.TextChoices):
        NONE = "none", "None"
        DOG = "dog", "Dog"
        VIRUS = "virus", "Virus"

    slug = models.SlugField(max_length=80, unique=True, db_index=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    title = models.CharField(max_length=160)
    title_de = models.CharField(max_length=160, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=160, blank=True)
    address = models.CharField(max_length=200, blank=True)
    zivilstand = models.CharField(max_length=40, blank=True)
    zivilstand_de = models.CharField(max_length=40, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    summary = models.TextField(blank=True)
    summary_de = models.TextField(blank=True)
    photo = models.ForeignKey(
        MediaAsset, null=True, blank=True, on_delete=models.PROTECT, related_name="people"
    )
    photo_funny = models.ForeignKey(
        MediaAsset,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="people_funny",
        help_text="Profile picture for the active funny theme; falls back to the theme default.",
    )
    active_funny_theme = models.CharField(
        max_length=20,
        choices=FunnyTheme.choices,
        default=FunnyTheme.DOG,
        help_text="Which funny theme (besides Normal) is selectable on the public site.",
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class AccessKey(models.Model):
    """Time-limited access token that unblurs the public CV's sensitive fields.

    Admins generate a key with an ``expires_at`` date and share the URL
    ``https://<host>/?key=<token>`` with the requester. The frontend stores
    the token in localStorage and forwards it on each ``GET /api/cv/`` call.
    """

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="access_keys")
    token = models.CharField(
        max_length=64, unique=True, db_index=True, default=_generate_access_token
    )
    label = models.CharField(max_length=120, blank=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"AccessKey<{self.label or self.token[:8]} expires={self.expires_at.isoformat()}>"

    @property
    def is_valid(self) -> bool:
        return self.is_active and self.expires_at > timezone.now()


class Readme(Orderable):
    """A per-application "README" cover document, authored in Markdown.

    Each job application gets its own named document. The body supports
    Mermaid diagrams (rendered client-side to SVG for the PDF export) and a
    small set of ``{{placeholder}}`` tokens resolved at render time:
    ``{{access_url}}``, ``{{expires_at}}``, ``{{version}}`` and ``{{updated}}``.
    Bodies are bilingual (``content`` = English, ``content_de`` = German),
    mirroring the dual-field strategy used across the CV models.
    """

    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="readmes")
    name = models.CharField(max_length=160, help_text="Application/company label.")
    content = models.TextField(blank=True)
    content_de = models.TextField(blank=True)
    version = models.CharField(max_length=40, default="v1.0.0")
    # Motivation letter — a second per-application document (same {{badges}} token,
    # whose first chip is the editable application reference below).
    letter_content = models.TextField(blank=True)
    letter_content_de = models.TextField(blank=True)
    letter_reference = models.CharField(max_length=120, blank=True)
    access_key = models.ForeignKey(
        AccessKey,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="readmes",
        help_text="Source for the auto-filled access URL and expiry date.",
    )

    def __str__(self) -> str:
        return self.name


class SkillCategory(Orderable):
    name = models.CharField(max_length=80, unique=True)
    name_de = models.CharField(max_length=80, blank=True)
    slug = models.SlugField(max_length=80, unique=True, db_index=True)

    class Meta(Orderable.Meta):
        verbose_name_plural = "skill categories"

    def __str__(self) -> str:
        return self.name


class Skill(Orderable):
    name = models.CharField(max_length=80)
    name_de = models.CharField(max_length=80, blank=True)
    category = models.ForeignKey(SkillCategory, on_delete=models.PROTECT, related_name="skills")
    level = models.PositiveSmallIntegerField(default=3, help_text="1-5 proficiency")
    technologies = models.ManyToManyField(Technology, blank=True, related_name="skills")
    show_in_pdf = models.BooleanField(
        default=True, help_text="Include this skill in the exported CV PDF."
    )

    class Meta(Orderable.Meta):
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="unique_skill_per_category"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.category.name})"


class Experience(Orderable):
    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="experiences")
    role = models.CharField(max_length=160)
    role_de = models.CharField(max_length=160, blank=True)
    company = models.CharField(max_length=160)
    location = models.CharField(max_length=160, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank for current")
    description = models.TextField(blank=True)
    description_de = models.TextField(blank=True)
    technologies = models.ManyToManyField(Technology, blank=True, related_name="experiences")
    media = models.ForeignKey(
        MediaAsset,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="experiences",
    )

    class Meta(Orderable.Meta):
        ordering = ["-start_date", "order"]
        indexes = [models.Index(fields=["-start_date"])]

    def __str__(self) -> str:
        return f"{self.role} @ {self.company}"


class Education(Orderable):
    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="educations")
    degree = models.CharField(max_length=160)
    degree_de = models.CharField(max_length=160, blank=True)
    institution = models.CharField(max_length=160)
    location = models.CharField(max_length=160, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    description_de = models.TextField(blank=True)
    technologies = models.ManyToManyField(Technology, blank=True, related_name="educations")
    media = models.ForeignKey(
        MediaAsset,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="educations",
    )

    class Meta(Orderable.Meta):
        ordering = ["-start_date", "order"]

    def __str__(self) -> str:
        return f"{self.degree} — {self.institution}"


class Certificate(Orderable):
    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="certificates")
    experience = models.ForeignKey(
        "Experience",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="certificates",
    )
    education = models.ForeignKey(
        "Education",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="certificates",
    )
    name = models.CharField(max_length=200)
    name_de = models.CharField(max_length=200, blank=True)
    issuer = models.CharField(max_length=160)
    issue_date = models.DateField()
    description = models.TextField(blank=True)
    description_de = models.TextField(blank=True)
    technologies = models.ManyToManyField(Technology, blank=True, related_name="certificates")
    media = models.ForeignKey(
        MediaAsset, null=True, blank=True, on_delete=models.PROTECT, related_name="certificates"
    )

    class Meta(Orderable.Meta):
        ordering = ["-issue_date", "order"]

    def __str__(self) -> str:
        return f"{self.name} ({self.issuer})"


class Project(Orderable):
    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="projects")
    name = models.CharField(max_length=160)
    name_de = models.CharField(max_length=160, blank=True)
    slug = models.SlugField(max_length=160, unique=True, db_index=True)
    summary = models.CharField(max_length=240, blank=True)
    summary_de = models.CharField(max_length=240, blank=True)
    description = models.TextField(blank=True)
    description_de = models.TextField(blank=True)
    url = models.URLField(blank=True)
    repo_url = models.URLField(blank=True)
    technologies = models.ManyToManyField(Technology, blank=True, related_name="projects")
    media = models.ManyToManyField(MediaAsset, blank=True, related_name="projects")

    def __str__(self) -> str:
        return self.name


class SocialLink(Orderable):
    class Platform(models.TextChoices):
        GITHUB = "github", "GitHub"
        LINKEDIN = "linkedin", "LinkedIn"
        XING = "xing", "Xing"
        EMAIL = "email", "Email"
        WEBSITE = "website", "Website"
        OTHER = "other", "Other"

    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="social_links")
    platform = models.CharField(max_length=20, choices=Platform.choices)
    label = models.CharField(max_length=80, blank=True)
    url = models.URLField()

    def __str__(self) -> str:
        return f"{self.platform}: {self.url}"


class TimelineEntry(Orderable):
    """A manually anchored milestone on the public timeline.

    Distinct from auto-derived entries (which the frontend assembles from
    experiences/education/certificates/projects) — these are free-form
    annotations like sabbaticals, awards, or relocations.
    """

    class Kind(models.TextChoices):
        MILESTONE = "milestone", "Milestone"
        AWARD = "award", "Award"
        TRANSITION = "transition", "Transition"
        OTHER = "other", "Other"

    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="timeline_entries")
    date = models.DateField()
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.MILESTONE)
    title = models.CharField(max_length=160)
    title_de = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    description_de = models.TextField(blank=True)

    class Meta(Orderable.Meta):
        ordering = ["-date", "order"]
        verbose_name_plural = "timeline entries"

    def __str__(self) -> str:
        return f"{self.date.isoformat()}: {self.title}"
