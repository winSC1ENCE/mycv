"""DRF serializers for CV entities.

The :class:`PersonDetailSerializer` returns a fully nested payload so the
frontend can render the whole CV from a single ``GET /api/cv/`` call.
Individual entity endpoints exist for admin/filter usage in later phases.

Write serializers (``*WriteSerializer``) are flat with FK fields as IDs,
used by admin ``create``/``update``/``partial_update`` actions.
"""

from __future__ import annotations

from typing import Any

from django.utils import timezone
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
        fields = ["id", "name", "slug", "category", "order"]


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
    media = MediaAssetSerializer(read_only=True)

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
            "media",
            "order",
            "is_published",
        ]

    def to_representation(self, instance: models.Experience) -> Any:
        data = super().to_representation(instance)
        granted: bool = self.context.get("access_granted", False)
        if not granted and data.get("media"):
            data["media"]["url"] = ""
        return data


class EducationSerializer(serializers.ModelSerializer[models.Education]):
    technologies = TechnologySerializer(many=True, read_only=True)
    media = MediaAssetSerializer(read_only=True)

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
            "technologies",
            "media",
            "order",
            "is_published",
        ]

    def to_representation(self, instance: models.Education) -> Any:
        data = super().to_representation(instance)
        granted: bool = self.context.get("access_granted", False)
        if not granted and data.get("media"):
            data["media"]["url"] = ""
        return data


class CertificateSerializer(serializers.ModelSerializer[models.Certificate]):
    technologies = TechnologySerializer(many=True, read_only=True)
    media = MediaAssetSerializer(read_only=True)

    class Meta:
        model = models.Certificate
        fields = [
            "id",
            "experience",
            "education",
            "name",
            "name_de",
            "issuer",
            "issue_date",
            "description",
            "description_de",
            "technologies",
            "media",
            "order",
            "is_published",
        ]

    def to_representation(self, instance: models.Certificate) -> Any:
        data = super().to_representation(instance)
        granted: bool = self.context.get("access_granted", False)
        if not granted and data.get("media"):
            data["media"]["url"] = ""
        return data


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


_REDACTED: dict[str, Any] = {
    "email": "***@***.***",
    "phone": "••• ••• ••••",
    "address": "••• ••• ••• •••",
    "zivilstand": "•••••",
    "zivilstand_de": "•••••",
    "date_of_birth": None,
}


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
            "address",
            "zivilstand",
            "zivilstand_de",
            "date_of_birth",
            "summary",
            "summary_de",
            "photo",
            "active_funny_theme",
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

    def to_representation(self, instance: models.Person) -> Any:
        data = super().to_representation(instance)
        granted: bool = self.context.get("access_granted", False)
        data["access_granted"] = granted
        if not granted:
            for key, placeholder in _REDACTED.items():
                data[key] = placeholder
        return data


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
            "address",
            "zivilstand",
            "zivilstand_de",
            "date_of_birth",
            "summary",
            "summary_de",
            "photo",
            "active_funny_theme",
            "order",
            "is_published",
        ]


class AccessKeySerializer(serializers.ModelSerializer[models.AccessKey]):
    is_valid = serializers.BooleanField(read_only=True)  # type: ignore[assignment]

    class Meta:
        model = models.AccessKey
        fields = [
            "id",
            "person",
            "token",
            "label",
            "expires_at",
            "is_active",
            "created_at",
            "is_valid",
        ]
        read_only_fields = ["token", "created_at", "is_valid"]


class AccessKeyWriteSerializer(serializers.ModelSerializer[models.AccessKey]):
    class Meta:
        model = models.AccessKey
        fields = ["id", "person", "token", "label", "expires_at", "is_active"]
        read_only_fields = ["token"]


class ReadmeSerializer(serializers.ModelSerializer[models.Readme]):
    """Read payload for a README, including resolved placeholder values.

    ``access_url``/``expires_display``/``updated_display`` are computed so the
    frontend preview substitutes the same ``{{placeholder}}`` tokens the PDF
    backend does, keeping preview and export identical.
    """

    access_url = serializers.SerializerMethodField()
    expires_display = serializers.SerializerMethodField()
    updated_display = serializers.SerializerMethodField()

    class Meta:
        model = models.Readme
        fields = [
            "id",
            "name",
            "content",
            "content_de",
            "version",
            "access_key",
            "access_url",
            "expires_display",
            "updated_display",
            "order",
            "is_published",
            "created_at",
            "updated_at",
        ]

    def get_access_url(self, obj: models.Readme) -> str:
        if obj.access_key is None:
            return ""
        request = self.context.get("request")
        base = request.build_absolute_uri("/") if request is not None else "/"
        return f"{base}?key={obj.access_key.token}"

    def get_expires_display(self, obj: models.Readme) -> str:
        if obj.access_key is None:
            return ""
        return timezone.localtime(obj.access_key.expires_at).strftime("%d.%m.%Y %H:%M")

    def get_updated_display(self, obj: models.Readme) -> str:
        return timezone.localtime(obj.updated_at).strftime("%d.%m.%Y")


class ReadmeWriteSerializer(serializers.ModelSerializer[models.Readme]):
    person = serializers.PrimaryKeyRelatedField(
        queryset=models.Person.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = models.Readme
        fields = [
            "id",
            "person",
            "name",
            "content",
            "content_de",
            "version",
            "access_key",
            "order",
            "is_published",
        ]


class TechnologyWriteSerializer(serializers.ModelSerializer[models.Technology]):
    class Meta:
        model = models.Technology
        fields = ["id", "name", "slug", "category", "order", "is_published"]


class SkillCategoryWriteSerializer(serializers.ModelSerializer[models.SkillCategory]):
    class Meta:
        model = models.SkillCategory
        fields = ["id", "name", "name_de", "slug", "order", "is_published"]


class SkillWriteSerializer(serializers.ModelSerializer[models.Skill]):
    class Meta:
        model = models.Skill
        fields = [
            "id",
            "name",
            "name_de",
            "category",
            "level",
            "technologies",
            "order",
            "is_published",
        ]


class SocialLinkWriteSerializer(serializers.ModelSerializer[models.SocialLink]):
    person = serializers.PrimaryKeyRelatedField(
        queryset=models.Person.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = models.SocialLink
        fields = ["id", "person", "platform", "label", "url", "order", "is_published"]


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
            "media",
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
            "technologies",
            "media",
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
            "experience",
            "education",
            "name",
            "name_de",
            "issuer",
            "issue_date",
            "description",
            "description_de",
            "technologies",
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

    def validate_media(self, value: list[models.MediaAsset]) -> list[models.MediaAsset]:
        if len(value) > 6:
            raise serializers.ValidationError("Maximum 6 photos per project.")
        return value

    def _apply_media_order(self, media: list[models.MediaAsset]) -> None:
        """Persist the submitted gallery order onto each asset's ``order``.

        ``Project.media`` is a plain M2M, so ``.set()`` only stores membership.
        The read path orders by ``MediaAsset.order``, so we mirror the submitted
        positions there to make reordering visible.
        """
        for index, asset in enumerate(media):
            if asset.order != index:
                asset.order = index
                asset.save(update_fields=["order"])

    def create(self, validated_data: dict[str, Any]) -> models.Project:
        media = list(validated_data.get("media", []))
        instance = super().create(validated_data)
        self._apply_media_order(media)
        return instance

    def update(self, instance: models.Project, validated_data: dict[str, Any]) -> models.Project:
        media = validated_data.get("media")
        instance = super().update(instance, validated_data)
        if media is not None:  # PATCH may omit media → leave order untouched
            self._apply_media_order(list(media))
        return instance


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
