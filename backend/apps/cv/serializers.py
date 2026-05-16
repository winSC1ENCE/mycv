"""DRF serializers for CV entities.

The :class:`PersonDetailSerializer` returns a fully nested payload so the
frontend can render the whole CV from a single ``GET /api/cv/`` call.
Individual entity endpoints exist for admin/filter usage in later phases.

Write serializers (``*WriteSerializer``) are flat with FK fields as IDs,
used by admin ``create``/``update``/``partial_update`` actions.
"""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from . import models


class MediaAssetSerializer(serializers.ModelSerializer[models.MediaAsset]):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.MediaAsset
        fields = ["id", "url", "alt_text", "kind", "order"]

    def get_url(self, obj: models.MediaAsset) -> str:
        return obj.file.url if obj.file else ""


class MediaAssetWriteSerializer(serializers.ModelSerializer[models.MediaAsset]):
    class Meta:
        model = models.MediaAsset
        fields = ["id", "file", "alt_text", "kind", "order", "is_published"]


class TechnologySerializer(serializers.ModelSerializer[models.Technology]):
    class Meta:
        model = models.Technology
        fields = ["id", "name", "slug", "category", "icon", "order"]


class SkillSerializer(serializers.ModelSerializer[models.Skill]):
    technologies = TechnologySerializer(many=True, read_only=True)

    class Meta:
        model = models.Skill
        fields = ["id", "name", "name_de", "level", "technologies", "order"]


class SkillCategorySerializer(serializers.ModelSerializer[models.SkillCategory]):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = models.SkillCategory
        fields = ["id", "name", "name_de", "slug", "skills", "order"]


class ExperienceSerializer(serializers.ModelSerializer[models.Experience]):
    technologies = TechnologySerializer(many=True, read_only=True)

    class Meta:
        model = models.Experience
        fields = [
            "id",
            "role",
            "role_de",
            "company",
            "location",
            "start_date",
            "end_date",
            "description",
            "description_de",
            "technologies",
            "order",
            "is_published",
        ]


class EducationSerializer(serializers.ModelSerializer[models.Education]):
    class Meta:
        model = models.Education
        fields = [
            "id",
            "degree",
            "degree_de",
            "institution",
            "location",
            "start_date",
            "end_date",
            "description",
            "description_de",
            "order",
            "is_published",
        ]


class CertificateSerializer(serializers.ModelSerializer[models.Certificate]):
    media = MediaAssetSerializer(read_only=True)

    class Meta:
        model = models.Certificate
        fields = [
            "id",
            "name",
            "name_de",
            "issuer",
            "issue_date",
            "description",
            "description_de",
            "media",
            "order",
            "is_published",
        ]


class ProjectSerializer(serializers.ModelSerializer[models.Project]):
    technologies = TechnologySerializer(many=True, read_only=True)
    media = MediaAssetSerializer(many=True, read_only=True)

    class Meta:
        model = models.Project
        fields = [
            "id",
            "name",
            "name_de",
            "slug",
            "summary",
            "summary_de",
            "description",
            "description_de",
            "url",
            "repo_url",
            "technologies",
            "media",
            "order",
            "is_published",
        ]


class SocialLinkSerializer(serializers.ModelSerializer[models.SocialLink]):
    class Meta:
        model = models.SocialLink
        fields = ["id", "platform", "label", "url", "order"]


class TimelineEntrySerializer(serializers.ModelSerializer[models.TimelineEntry]):
    class Meta:
        model = models.TimelineEntry
        fields = [
            "id",
            "date",
            "kind",
            "title",
            "title_de",
            "description",
            "description_de",
            "order",
            "is_published",
        ]


class PersonDetailSerializer(serializers.ModelSerializer[models.Person]):
    """Full CV payload returned by ``GET /api/cv/``."""

    photo = MediaAssetSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    social_links = SocialLinkSerializer(many=True, read_only=True)
    timeline_entries = TimelineEntrySerializer(many=True, read_only=True)
    skill_categories = serializers.SerializerMethodField()

    class Meta:
        model = models.Person
        fields = [
            "id",
            "slug",
            "first_name",
            "last_name",
            "full_name",
            "title",
            "title_de",
            "email",
            "phone",
            "location",
            "summary",
            "summary_de",
            "photo",
            "experiences",
            "educations",
            "certificates",
            "projects",
            "social_links",
            "timeline_entries",
            "skill_categories",
        ]

    def get_skill_categories(self, _obj: models.Person) -> list[Any]:
        qs = (
            models.SkillCategory.objects.filter(is_published=True)
            .prefetch_related("skills__technologies")
            .order_by("order", "id")
        )
        return SkillCategorySerializer(qs, many=True).data  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Write serializers — flat, FK fields as IDs, used for admin mutations
# ---------------------------------------------------------------------------


class PersonWriteSerializer(serializers.ModelSerializer[models.Person]):
    class Meta:
        model = models.Person
        fields = [
            "id",
            "slug",
            "first_name",
            "last_name",
            "title",
            "title_de",
            "email",
            "phone",
            "location",
            "summary",
            "summary_de",
            "photo",
            "order",
            "is_published",
        ]


class TechnologyWriteSerializer(serializers.ModelSerializer[models.Technology]):
    class Meta:
        model = models.Technology
        fields = ["id", "name", "slug", "category", "icon", "order", "is_published"]


class SkillCategoryWriteSerializer(serializers.ModelSerializer[models.SkillCategory]):
    class Meta:
        model = models.SkillCategory
        fields = ["id", "name", "name_de", "slug", "order", "is_published"]


class ExperienceWriteSerializer(serializers.ModelSerializer[models.Experience]):
    person = serializers.PrimaryKeyRelatedField(
        queryset=models.Person.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = models.Experience
        fields = [
            "id",
            "person",
            "role",
            "role_de",
            "company",
            "location",
            "start_date",
            "end_date",
            "description",
            "description_de",
            "technologies",
            "order",
            "is_published",
        ]


class EducationWriteSerializer(serializers.ModelSerializer[models.Education]):
    person = serializers.PrimaryKeyRelatedField(
        queryset=models.Person.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = models.Education
        fields = [
            "id",
            "person",
            "degree",
            "degree_de",
            "institution",
            "location",
            "start_date",
            "end_date",
            "description",
            "description_de",
            "order",
            "is_published",
        ]


class CertificateWriteSerializer(serializers.ModelSerializer[models.Certificate]):
    person = serializers.PrimaryKeyRelatedField(
        queryset=models.Person.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = models.Certificate
        fields = [
            "id",
            "person",
            "name",
            "name_de",
            "issuer",
            "issue_date",
            "description",
            "description_de",
            "media",
            "order",
            "is_published",
        ]


class ProjectWriteSerializer(serializers.ModelSerializer[models.Project]):
    person = serializers.PrimaryKeyRelatedField(
        queryset=models.Person.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = models.Project
        fields = [
            "id",
            "person",
            "name",
            "name_de",
            "slug",
            "summary",
            "summary_de",
            "description",
            "description_de",
            "url",
            "repo_url",
            "technologies",
            "media",
            "order",
            "is_published",
        ]


class TimelineEntryWriteSerializer(serializers.ModelSerializer[models.TimelineEntry]):
    person = serializers.PrimaryKeyRelatedField(
        queryset=models.Person.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = models.TimelineEntry
        fields = [
            "id",
            "person",
            "date",
            "kind",
            "title",
            "title_de",
            "description",
            "description_de",
            "order",
            "is_published",
        ]
