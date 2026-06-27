from django.urls import path

from .readme import ReadmePdfView
from .views import CvPdfView

urlpatterns: list[object] = [
    # Specific paths must precede the cv router's detail routes.
    path("cv/pdf/", CvPdfView.as_view(), name="cv-pdf"),
    path("admin/readmes/<int:pk>/pdf/", ReadmePdfView.as_view(), name="readme-pdf"),
]
