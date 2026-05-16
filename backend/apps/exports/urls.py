from django.urls import path

from .views import CvPdfView

urlpatterns = [
    path("cv/pdf/", CvPdfView.as_view(), name="cv-pdf"),
]
