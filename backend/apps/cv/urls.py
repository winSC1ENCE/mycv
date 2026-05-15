"""CV API router."""

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("cv", views.PersonViewSet, basename="cv")
router.register("experiences", views.ExperienceViewSet, basename="experience")
router.register("educations", views.EducationViewSet, basename="education")
router.register("certificates", views.CertificateViewSet, basename="certificate")
router.register("projects", views.ProjectViewSet, basename="project")
router.register("technologies", views.TechnologyViewSet, basename="technology")
router.register("skill-categories", views.SkillCategoryViewSet, basename="skill-category")
router.register("timeline", views.TimelineEntryViewSet, basename="timeline")

urlpatterns = router.urls
