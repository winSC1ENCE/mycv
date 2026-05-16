from django.contrib import admin

from . import models


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("full_name", "title", "email", "is_published")
    search_fields = ("first_name", "last_name", "email")


@admin.register(models.Technology)
class TechnologyAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "category", "order", "is_published")
    search_fields = ("name", "category")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(models.Skill)
class SkillAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "category", "level", "order")
    list_filter = ("category",)
    filter_horizontal = ("technologies",)


@admin.register(models.Experience)
class ExperienceAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("role", "company", "start_date", "end_date", "is_published")
    list_filter = ("company",)
    date_hierarchy = "start_date"
    filter_horizontal = ("technologies",)
    search_fields = ("role", "company")


@admin.register(models.Education)
class EducationAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("degree", "institution", "start_date", "end_date", "is_published")
    date_hierarchy = "start_date"
    search_fields = ("degree", "institution")


@admin.register(models.Certificate)
class CertificateAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "issuer", "issue_date", "experience", "education", "is_published")
    list_filter = ("experience", "education")
    date_hierarchy = "issue_date"
    autocomplete_fields = ("person", "experience", "education")


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "is_published", "order")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("technologies", "media")


@admin.register(models.SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("platform", "url", "order")
    list_filter = ("platform",)


@admin.register(models.TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("date", "title", "kind", "is_published")
    list_filter = ("kind",)
    date_hierarchy = "date"


@admin.register(models.MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("file", "kind", "alt_text", "order")
    list_filter = ("kind",)
