from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .tasks import create_and_email_export


@admin.site.admin_view
def export_all_assessments(request):
    messages.info(
        request,
        _(
            "Exporting assessments document. Download link will be sent to your email shortly."
        ),
    )
    create_and_email_export.delay([], request.user.id)
    return HttpResponseRedirect(
        reverse_lazy("admin:assessments_compliancecriticalityassessment_changelist")
    )
