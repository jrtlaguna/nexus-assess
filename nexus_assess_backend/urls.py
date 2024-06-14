from allauth.account.views import confirm_email
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    # Redirect root path to /admin/
    path("", lambda request: redirect("cca-admin/", permanent=False)),
    path("cca-admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        TemplateView.as_view(template_name="accounts/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    # v1 APIs
    path(
        "api/v1/",
        include(
            (
                [
                    path(
                        "auth/user/", include("users.urls")
                    ),  # this should be placed before dj_rest_auth.urls as it overrides some views
                    path("auth/", include("dj_rest_auth.urls")),
                    path(
                        "auth/registration/account-confirm-email/<str:key>/",
                        confirm_email,
                    ),
                    path(
                        "auth/registration/", include("dj_rest_auth.registration.urls")
                    ),
                    path("assessment/", include("assessments.urls")),
                    path("", include("core.urls")),
                ],
                "v1",
            ),
            namespace="v1",
        ),
    ),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Swagger
api_info = openapi.Info(
    title="Nexus Criticality Assessment Backend API",
    default_version="v1",
    description="API documentation for Nexus Criticality Assessment Backend",
)

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns += [
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api_docs"),
]


admin.site.site_header = "Nexus Criticality Assessment Backend"
admin.site.site_title = "Nexus Criticality Assessment Backend Admin Portal"
admin.site.index_title = "Nexus Criticality Assessment Backend Admin"
