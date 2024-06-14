from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .api.v1 import views
from .views import export_all_assessments

router = DefaultRouter()
router.register("", views.CcaApiModelViewset, basename="cca")

urlpatterns = [
    path(
        "export-all-asessments", export_all_assessments, name="export_all_assessments"
    ),
    path("cca/", include(router.urls), name="cca"),
]
