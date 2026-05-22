from django.urls import path  # noqa: F401 — kept for re-enable; PDF route disabled (refactoring_12)

# PDF export disabled (refactoring_12) — uncomment both lines below to re-enable.
# from .views import CvPdfView

urlpatterns: list[object] = [
    # path("cv/pdf/", CvPdfView.as_view(), name="cv-pdf"),
]
