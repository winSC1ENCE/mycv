from django.urls import path

from .readme import ReadmePdfView
from .views import CertificatesPdfView, CvPdfView

urlpatterns: list[object] = [
    # Specific paths must precede the cv router's detail routes.
    path("cv/pdf/", CvPdfView.as_view(), name="cv-pdf"),
    path("cv/certificates/pdf/", CertificatesPdfView.as_view(), name="cv-certificates-pdf"),
    path("admin/readmes/<int:pk>/pdf/", ReadmePdfView.as_view(), name="readme-pdf"),
]
