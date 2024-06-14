import zipfile
from io import BytesIO, StringIO

from celery import shared_task

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from core.utils import get_base_email_vars

from .applogic.csv_export_applogic import convert_to_dataframe

User = get_user_model()


@shared_task(rate_limit="1/m")
def get_form_results(cca_id):
    from requirements.models import Requirement

    from .applogic.form_results_applogic import get_form_results
    from .models import ComplianceCriticalityAssessment

    try:
        cca = ComplianceCriticalityAssessment.objects.get(id=cca_id)
        requirements = get_form_results(cca)

        data = {
            "success": True,
            "requirement_ids": list(requirements.values_list("id", flat=True)),
            "message": _(f"Output 2 generated successfully."),
        }
        return data
    except Exception as e:
        return {"success": False, "message": _(f"Error getting form results: {str(e)}")}


@shared_task(rate_limit="1/m")
def create_output_1(signature_data, cca_id):
    from requirements.models import Requirement

    from .applogic.generate_output_1 import generate_output_1
    from .models import ComplianceCriticalityAssessment

    try:
        requirement_ids = signature_data.get("requirement_ids", None)
        if requirement_ids is not None and signature_data.get("success"):
            requirements = Requirement.objects.filter(id__in=requirement_ids)
            cca = ComplianceCriticalityAssessment.objects.get(id=cca_id)
            generate_output_1(cca, requirements)

            data = {
                "success": True,
                "requirement_ids": list(requirements.values_list("id", flat=True)),
                "message": _(f"Output 1 generated successfully."),
            }
        else:
            data = {"success": False, "message": _(f"Requirements data missing.")}
        return data
    except Exception as e:
        return {"success": False, "message": _(f"Error generating Output 1: {str(e)}")}


@shared_task(rate_limit="1/m")
def create_output_2(signature_data, cca_id):
    from requirements.models import Requirement

    from .applogic.generate_output_2 import generate_output_2
    from .models import ComplianceCriticalityAssessment

    try:
        requirement_ids = signature_data.get("requirement_ids", None)
        if requirement_ids is not None and signature_data.get("success"):
            requirements = Requirement.objects.filter(id__in=requirement_ids)
            cca = ComplianceCriticalityAssessment.objects.get(id=cca_id)
            generate_output_2(cca, requirements)

            data = {"success": True, "message": _(f"Output 2 generated successfully.")}
        else:
            data = {"success": False, "message": _(f"Requirements data missing.")}
        return data
    except Exception as e:
        return {"success": False, "message": _(f"Error generating Output 2: {str(e)}")}


@shared_task(rate_limit="1/m")
def create_docx(signature_data, cca_id):
    from .applogic.generate_docx import generate_docx_output
    from .models import ComplianceCriticalityAssessment

    try:
        cca = ComplianceCriticalityAssessment.objects.get(id=cca_id)
        generate_docx_output(cca)

        data = {"success": True, "message": _(f"CCA Document generated successfully.")}
        return data
    except Exception as e:
        return {
            "success": False,
            "message": _(f"Error generating CCA Document: {str(e)}"),
        }


@shared_task(rate_limit="1/m")
def compress_reports_and_save_to_model(signature_data, cca_id):
    from .models import ComplianceCriticalityAssessment

    try:
        cca = ComplianceCriticalityAssessment.objects.get(id=cca_id)

        # File keys in storage
        field_names = ["output_xlsm_1", "output_xlsm_2", "output_cca_doc"]
        file_keys = []

        for name in field_names:
            try:
                file_keys.append(getattr(cca.report, name).file.obj.key)
            except ValueError:
                pass

        # open/read files and compress them
        with BytesIO() as zip_buffer:
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                for file_key in file_keys:
                    # Download the file from storage
                    file_content = default_storage.open(file_key).read()

                    # Add the file to the zip archive
                    zip_file.writestr(file_key, file_content)

            # Save the compressed file to the model field
            zip_buffer.seek(0)
            cca.report.compressed_reports.save(
                f"reports.zip", ContentFile(zip_buffer.read())
            )

        data = {"success": True, "message": _(f"Reports have been compiled and zipped")}
        return data
    except Exception as e:
        return {"success": False, "message": _(f"Error compiling reports: {str(e)}")}


@shared_task(rate_limit="1/m")
def send_form_reports_email(signature_data, cca_id):
    from .models import ComplianceCriticalityAssessment, Report

    try:
        cca = ComplianceCriticalityAssessment.objects.get(id=cca_id)
        report = Report.objects.get(cca=cca)
        data = get_base_email_vars()
        data.update({"url": report.compressed_reports.url, "form": cca})
        context = {
            "current_site": Site.objects.get_current(),
            "protocol": "http",
            "title": "Report Ready For Download",
        }
        template = "assessments/email/form_reports_notification.html"
        context.update(data)
        html_content = render_to_string(template, context)
        text_content = strip_tags(html_content)

        # send to drafter and approvers
        recipients = {cca.drafted_by.email}
        if cca.business_owner and cca.business_owner.email:
            recipients.add(cca.business_owner.email)
        if cca.system_owner and cca.system_owner.email:
            recipients.add(cca.system_owner.email)
        if (
            cca.it_risk_management_and_compliance
            and cca.it_risk_management_and_compliance.email
        ):
            recipients.add(cca.it_risk_management_and_compliance.email)
        recipients = list(recipients)

        send_mail(
            subject="Nexus - Form Report Ready For Download Notification",
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
            html_message=html_content,
        )

        data = {
            "success": True,
            "message": _(f"Reports for Form #{cca_id} have been sent to email"),
        }
        return data
    except Exception as e:
        return {
            "success": False,
            "message": _(f"Error sending form reports download notification: {str(e)}"),
        }


@shared_task(rate_limit="1/m")
def create_assessment_export(assessment_id_list, user_id):
    from .models import AssessmentExport, ComplianceCriticalityAssessment

    try:
        if not assessment_id_list:
            queryset = ComplianceCriticalityAssessment.objects.all()
        else:
            queryset = ComplianceCriticalityAssessment.objects.filter(
                id__in=assessment_id_list
            )
        df, filename = convert_to_dataframe(queryset)

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        csv_content = csv_buffer.getvalue().encode("utf-8")
        csv_file = ContentFile(csv_content)

        user = User.objects.get(id=user_id)

        export = AssessmentExport.objects.create(
            exported_by=user,
        )
        export.document_file.save(filename, csv_file)

        return export
    except Exception as e:
        return f"Something went wrong. Error: {str(e)}"


@shared_task(rate_limit="1/m")
def create_and_email_export(assessment_id_list, user_id):
    try:
        export = create_assessment_export(assessment_id_list, user_id)
        user = User.objects.get(id=user_id)
        data = get_base_email_vars()
        data.update({"url": export.document_file.url, "user": user})

        template = "assessments/email/export_finished_notification.html"
        context = {
            "current_site": Site.objects.get_current(),
            "protocol": "http",
            "title": "CCA Export Ready For Download",
        }
        context.update(data)
        html_content = render_to_string(template, context)
        text_content = strip_tags(html_content)

        send_mail(
            subject="Nexus - CCA Export Ready For Download Notification",
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_content,
        )
        return
    except Exception as e:
        return f"Something went wrong. Error: {str(e)}"
