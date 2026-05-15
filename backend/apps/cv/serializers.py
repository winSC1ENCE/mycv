"""DRF serializers for CV entities.

The :class:`PersonDetailSerializer` returns a fully nested payload so the
frontend can render the whole CV from a single ``GET /api/cv/`` call.
Individual entity endpoints exist for admin/filter usage in later phases.
"""

from __future__ import annotations

from rest_framework import serializers

from . import models


class MediaAssetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.MediaAsset
        fields = ["id", "url", "alt_text", "kind", "order"]

    def get_url(self, obj: models.MediaAsset) -> str:
        return obj.file.url if obj.file else ""


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Technology
        fields = ["id", "name", "slug", "category", "icon", "order"]


class SkillSerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True, read_only=True)

    class Meta:
        model = models.Skill
        fields = ["id", "name", "name_de", "level", "technologies", "order"]


class SkillCategorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = models.SkillCategory
        fields = ["id", "name", "name_de", "slug", "skills", "order"]


class ExperienceSerializer(serializers.ModelSerializer):
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


class EducationSerializer(serializers.ModelSerializer):
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


class CertificateSerializer(serializers.ModelSerializer):
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


class ProjectSerializer(serializers.ModelSerializer):
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


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SocialLink
        fields = ["id", "platform", "label", "url", "order"]


class TimelineEntrySerializer(serializers.ModelSerializer):
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


class PersonDetailSerializer(serializers.ModelSerializer):
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

    def get_skill_categories(self, _obj: models.Person) -> list[dict]:
        qs = (
            models.SkillCategory.objects.filter(is_published=True)
            .prefetch_related("skills__technologies")
            .order_by("order", "id")
        )
        return SkillCategorySerializer(qs, many=True).data
