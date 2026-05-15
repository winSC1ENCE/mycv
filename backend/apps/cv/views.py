"""DRF views for CV entities — read-only for public, full CRUD for admin/staff."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import parsers, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from . import models, serializers
from .permissions import IsAdminOrReadOnly

_SerializerClass = type[BaseSerializer[Any]]


def _is_staff(request: Request) -> bool:
    return bool(request.user and request.user.is_staff)


class PersonViewSet(viewsets.ModelViewSet[models.Person]):
    """The CV root resource.

    ``GET /api/cv/`` returns the primary published person (not a list).
    Staff can retrieve any person by slug via ``GET /api/cv/<slug>/``.
    """

    queryset = models.Person.objects.prefetch_related(
        "experiences__technologies",
        "educations",
        "certificates__media",
        "projects__technologies",
        "projects__media",
        "social_links",
        "timeline_entries",
    )
    serializer_class = serializers.PersonDetailSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[models.Person]:
        qs = super().get_queryset()
        if not _is_staff(self.request):
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self) -> _SerializerClass:
        if self.action in ("create", "update", "partial_update"):
            return serializers.PersonWriteSerializer
        return serializers.PersonDetailSerializer

    @extend_schema(
        summary="Return the primary published person (first by `order`).",
        responses=serializers.PersonDetailSerializer,
    )
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        person = self.get_queryset().first()
        if person is None:
            raise NotFound("No published Person record exists.")
        return Response(self.get_serializer(person).data, status=status.HTTP_200_OK)


class ExperienceViewSet(viewsets.ModelViewSet[models.Experience]):
    queryset = models.Experience.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["company"]

    def get_queryset(self) -> QuerySet[models.Experience]:
        qs = super().get_queryset()
        if not _is_staff(self.request):
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self) -> _SerializerClass:
        if self.action in ("create", "update", "partial_update"):
            return serializers.ExperienceWriteSerializer
        return serializers.ExperienceSerializer


class EducationViewSet(viewsets.ModelViewSet[models.Education]):
    queryset = models.Education.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self) -> QuerySet[models.Education]:
        qs = super().get_queryset()
        if not _is_staff(self.request):
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self) -> _SerializerClass:
        if self.action in ("create", "update", "partial_update"):
            return serializers.EducationWriteSerializer
        return serializers.EducationSerializer


class CertificateViewSet(viewsets.ModelViewSet[models.Certificate]):
    queryset = models.Certificate.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self) -> QuerySet[models.Certificate]:
        qs = super().get_queryset()
        if not _is_staff(self.request):
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self) -> _SerializerClass:
        if self.action in ("create", "update", "partial_update"):
            return serializers.CertificateWriteSerializer
        return serializers.CertificateSerializer


class ProjectViewSet(viewsets.ModelViewSet[models.Project]):
    queryset = models.Project.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[models.Project]:
        qs = super().get_queryset()
        if not _is_staff(self.request):
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self) -> _SerializerClass:
        if self.action in ("create", "update", "partial_update"):
            return serializers.ProjectWriteSerializer
        return serializers.ProjectSerializer


class TechnologyViewSet(viewsets.ModelViewSet[models.Technology]):
    queryset = models.Technology.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    filterset_fields = ["category"]

    def get_queryset(self) -> QuerySet[models.Technology]:
        qs = super().get_queryset()
        if not _is_staff(self.request):
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self) -> _SerializerClass:
        if self.action in ("create", "update", "partial_update"):
            return serializers.TechnologyWriteSerializer
        return serializers.TechnologySerializer


class SkillCategoryViewSet(viewsets.ModelViewSet[models.SkillCategory]):
    queryset = models.SkillCategory.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[models.SkillCategory]:
        qs = super().get_queryset()
        if not _is_staff(self.request):
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self) -> _SerializerClass:
        if self.action in ("create", "update", "partial_update"):
            return serializers.SkillCategoryWriteSerializer
        return serializers.SkillCategorySerializer


class TimelineEntryViewSet(viewsets.ModelViewSet[models.TimelineEntry]):
    queryset = models.TimelineEntry.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self) -> QuerySet[models.TimelineEntry]:
        qs = super().get_queryset()
        if not _is_staff(self.request):
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self) -> _SerializerClass:
        if self.action in ("create", "update", "partial_update"):
            return serializers.TimelineEntryWriteSerializer
        return serializers.TimelineEntrySerializer


class MediaAssetViewSet(viewsets.ModelViewSet[models.MediaAsset]):
    queryset = models.MediaAsset.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self) -> QuerySet[models.MediaAsset]:
        qs = models.MediaAsset.objects.all()
        if not _is_staff(self.request):
            qs = qs.filter(is_published=True)
        return qs

    def get_serializer_class(self) -> _SerializerClass:
        if self.action in ("create", "update", "partial_update"):
            return serializers.MediaAssetWriteSerializer
        return serializers.MediaAssetSerializer
