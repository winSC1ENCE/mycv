from django.urls import path

from .readme import ReadmePdfView

# CV PDF export disabled (refactoring_12) — uncomment both lines below to re-enable.
# from .views import CvPdfView

urlpatterns: list[object] = [
    # path("cv/pdf/", CvPdfView.as_view(), name="cv-pdf"),
    # Specific path must precede the cv router's admin/readmes/<pk>/ detail route.
    path("admin/readmes/<int:pk>/pdf/", ReadmePdfView.as_view(), name="readme-pdf"),
]
