"""Read-only DRF views for Phase 1."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from . import models, serializers


class PublishedQuerysetMixin:
    """Restrict listings to ``is_published=True`` rows."""

    model: type[models.Orderable]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return self.model.objects.filter(is_published=True)


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    """The CV root resource. ``GET /api/cv/`` returns the primary person; the
    list endpoint surfaces all published persons for completeness."""

    queryset = models.Person.objects.filter(is_published=True).prefetch_related(
        "experiences__technologies",
        "educations",
        "certificates__media",
        "projects__technologies",
        "projects__media",
        "social_links",
        "timeline_entries",
    )
    serializer_class = serializers.PersonDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    @extend_schema(
        summary="Return the primary published person (first by `order`).",
        responses=serializers.PersonDetailSerializer,
    )
    def list(self, request: Request, *args: object, **kwargs: object) -> Response:
        person = self.get_queryset().first()
        if person is None:
            raise NotFound("No published Person record exists.")
        return Response(self.get_serializer(person).data, status=status.HTTP_200_OK)


class ExperienceViewSet(PublishedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.Experience
    serializer_class = serializers.ExperienceSerializer
    permission_classes = [AllowAny]
    filterset_fields = ["company"]


class EducationViewSet(PublishedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.Education
    serializer_class = serializers.EducationSerializer
    permission_classes = [AllowAny]


class CertificateViewSet(PublishedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.Certificate
    serializer_class = serializers.CertificateSerializer
    permission_classes = [AllowAny]


class ProjectViewSet(PublishedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.Project
    serializer_class = serializers.ProjectSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class TechnologyViewSet(PublishedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.Technology
    serializer_class = serializers.TechnologySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filterset_fields = ["category"]


class SkillCategoryViewSet(PublishedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.SkillCategory
    serializer_class = serializers.SkillCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class TimelineEntryViewSet(PublishedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    model = models.TimelineEntry
    serializer_class = serializers.TimelineEntrySerializer
    permission_classes = [AllowAny]
