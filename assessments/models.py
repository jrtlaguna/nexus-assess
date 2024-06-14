import os

from celery import chain
from django_extensions.db.models import TimeStampedModel

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.models import OPTIONAL

from . import applogic as assessment_applogic
from .tasks import (
    compress_reports_and_save_to_model,
    create_docx,
    create_output_1,
    create_output_2,
    get_form_results,
    send_form_reports_email,
)


def upload_report_to(instance, filename):
    directory = os.path.join("reports", f"{slugify(instance.cca.name)}")
    if not os.path.exists(directory):
        os.makedirs(directory)

    return os.path.join(directory, filename)


class ComplianceCriticalityAssessment(TimeStampedModel):
    class SolutionType(models.TextChoices):
        APPLICATION = "application", _("Application")
        INFRASTRUCTURE = "infrastructure", _("Infrastructure Platform")
        MIDDLEWARE = "middleware", _("Middleware")
        OTHER = "other", _("Other")

    class SolutionClassification(models.TextChoices):
        CUSTOM = "custom", _("Custom")
        CONFIGURABLE = "configurable", _("Configurable")
        NON_CONFIGURABLE = "non_configurable", _("Non-configurable (out-of-the-box)")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        FOR_REVIEW = "for_review", _("For Review")
        FOR_REVISION = "for_revision", _("For Revision")
        APPROVED = "approved", _("Approved")

    class HostingAndType(models.TextChoices):
        THIRD_PARTY = "third_party", _("Third Party Hosting")
        ON_PREMISES = "on_premises", _("On-Premises")
        WEBSITE = "website", _("Website (Public)")
        SAAS = "saas", _("Software As a Service (Saas)")
        PAAS = "paas", _("Platform As a Service (Paas)")
        IAAS = "iaas", _("Infrastructure As a Service (IAAS)")

    name = models.CharField(_("Form Name"), max_length=256, **OPTIONAL)

    # Ownership
    company = models.ForeignKey(
        "users.Company", verbose_name=_("Company"), on_delete=models.CASCADE, null=True
    )
    drafted_by = models.ForeignKey(
        "users.User",
        verbose_name=_("Drafted By"),
        related_name="cca_drafts",
        on_delete=models.CASCADE,
        null=True,
    )
    business_owner = models.ForeignKey(
        "users.User",
        verbose_name=_("Business Owner"),
        related_name="cca_business_owner",
        on_delete=models.CASCADE,
        null=True,
    )
    system_owner = models.ForeignKey(
        "users.User",
        verbose_name=_("System Owner"),
        related_name="cca_system_owner",
        on_delete=models.CASCADE,
        null=True,
    )
    it_risk_management_and_compliance = models.ForeignKey(
        "users.User",
        verbose_name=_("IT Risk Management and Compliance"),
        related_name="cca_it_risk_management_and_compliance",
        on_delete=models.CASCADE,
        null=True,
    )

    # Statuses
    status = models.CharField(
        _("Status"), max_length=50, choices=Status.choices, default=Status.DRAFT
    )
    approved_by_business_owner = models.BooleanField(
        _("Approved by Business Owner"), default=None, **OPTIONAL
    )
    datetime_approved_by_business_owner = models.DateTimeField(
        _("Approved on"), **OPTIONAL
    )
    approved_by_system_owner = models.BooleanField(
        _("Approved by System Owner"), default=None, **OPTIONAL
    )
    datetime_approved_by_system_owner = models.DateTimeField(
        _("Approved on"), **OPTIONAL
    )
    approved_by_it_risk_management_and_compliance = models.BooleanField(
        _("Approved by IT Risk Management and Compliance"), default=None, **OPTIONAL
    )
    datetime_approved_by_it_risk_management_and_compliance = models.DateTimeField(
        _("Approved on"), **OPTIONAL
    )

    # Solution Identification
    solution_name = models.CharField(_("Solution Name"), max_length=256)
    solution_version = models.CharField(
        _("Software Release / Version, as applicable"), max_length=256, **OPTIONAL
    )
    vendor_name = models.CharField(_("Vendor Name"), max_length=256, null=True)
    solution_type = models.CharField(
        _("Solution Type"), max_length=50, choices=SolutionType.choices, null=True
    )
    other_solution_type = models.CharField(
        _("If other, please specify"), max_length=256, **OPTIONAL
    )
    hosting_and_type = models.CharField(
        _("Hosting and Type"), max_length=50, choices=HostingAndType.choices, null=True
    )
    server_host = models.CharField(
        _("Server Host / Location"), max_length=256, null=True
    )
    solution_classification = models.CharField(
        _("Solution Classification"),
        max_length=50,
        choices=SolutionClassification.choices,
        null=True,
    )

    # CCA Questionnaire Questions
    solution_description = models.TextField(
        _("Solution Description and Intended Use"), **OPTIONAL
    )
    gxp_impact = models.JSONField(
        _("GxP Impact"),
        validators=[assessment_applogic.validate_gxp_impact_json],
        default=assessment_applogic.get_default_gxp_impact_json_value,
    )
    gxp_eres = models.JSONField(
        _("GxP Electronic Records (ER) and Electronic Signatures (ES) Applicability"),
        validators=[assessment_applogic.validate_gxp_eres_json],
        default=assessment_applogic.get_default_gxp_eres_json_value,
    )
    sox_impact = models.JSONField(
        _("SOX Impact"),
        validators=[assessment_applogic.validate_sox_impact_json],
        default=assessment_applogic.get_default_sox_impact_json_value,
    )
    privacy_impact = models.JSONField(
        _("Privacy Impact"),
        validators=[assessment_applogic.validate_privacy_impact_json],
        default=assessment_applogic.get_default_privacy_impact_json_value,
    )
    data_classification = models.JSONField(
        _("Data Classification"),
        validators=[assessment_applogic.validate_data_classification_json],
        default=assessment_applogic.get_default_data_classification_json_value,
    )
    business_impact = models.JSONField(
        _("Business Impact"),
        validators=[assessment_applogic.validate_business_impact_json],
        default=assessment_applogic.get_default_business_impact_json_value,
    )

    # Summary and Rating
    summary = models.JSONField(
        _("Summary"),
        validators=[assessment_applogic.validate_summary_json],
        default=assessment_applogic.get_default_summary_json_value,
    )
    rating = models.JSONField(
        _("Compliance Criticality Rating"),
        validators=[assessment_applogic.validate_rating_json],
        default=assessment_applogic.get_default_rating_json_value,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Compliance Criticality Assessment")
        verbose_name_plural = _("Compliance Criticality Assessments")

    @property
    def solution_type_display(self):
        if self.solution_type == self.SolutionType.OTHER:
            return self.other_solution_type
        return self.get_solution_type_display()

    def calculate_summary_and_rating(self):
        serialized_data = model_to_dict(self)
        self.summary = assessment_applogic.calculate_summary(serialized_data)
        self.rating = assessment_applogic.calculate_rating(self.summary)

    def save(self, *args, **kwargs):
        prev_status = self.status
        create_name = False
        if self.pk is None:
            create_name = True

        self.calculate_summary_and_rating()
        super().save(*args, **kwargs)

        if create_name and not self.name:
            self.name = f"Form #{self.id}"
            super().save(update_fields=["name"])

        approval_statuses = [
            self.approved_by_business_owner,
            self.approved_by_system_owner,
            self.approved_by_it_risk_management_and_compliance,
        ]

        all_reviewed = all(status is not None for status in approval_statuses)
        all_approved = all(status is True for status in approval_statuses)
        any_rejected = any(status is False for status in approval_statuses)

        if all_reviewed and all_approved:
            self.transition_to_approved(prev_status)
        elif all_reviewed and any_rejected:
            self.transition_to_for_revision(prev_status)

    def run_generate_reports_chain(self):
        tasks_chain = chain(
            get_form_results.s(self.id),
            create_output_1.s(self.id),
            create_output_2.s(self.id),
            create_docx.s(self.id),
            compress_reports_and_save_to_model.s(self.id),
            send_form_reports_email.s(self.id),
        )

        tasks_chain.apply_async()

    def reset_approval_states(self):
        self.approved_by_business_owner = None
        self.datetime_approved_by_business_owner = None
        self.approved_by_system_owner = None
        self.datetime_approved_by_system_owner = None
        self.approved_by_it_risk_management_and_compliance = None
        self.datetime_approved_by_it_risk_management_and_compliance = None

        super().save(
            update_fields=[
                "approved_by_business_owner",
                "datetime_approved_by_business_owner",
                "approved_by_system_owner",
                "datetime_approved_by_system_owner",
                "approved_by_it_risk_management_and_compliance",
                "datetime_approved_by_it_risk_management_and_compliance",
            ]
        )

    def transition_to_draft(self, prev_status=None):
        self.status = self.Status.DRAFT
        super().save(update_fields=["status"])
        return self

    def transition_to_for_review(self, prev_status=None):
        self.status = self.Status.FOR_REVIEW
        super().save(update_fields=["status"])
        if prev_status == self.Status.DRAFT:
            self.reset_approval_states()
        return self

    def transition_to_for_revision(self, prev_status=None):
        self.status = ComplianceCriticalityAssessment.Status.FOR_REVISION
        super().save(update_fields=["status"])
        return self

    def transition_to_approved(self, prev_status=None):
        self.status = self.Status.APPROVED
        super().save(update_fields=["status"])

        if prev_status != self.Status.APPROVED:
            self.run_generate_reports_chain()
        return self


@receiver(post_save, sender=ComplianceCriticalityAssessment)
def create_report_on_cca_creation(sender, instance, created, **kwargs):
    if created:
        Report.objects.create(cca=instance)
    return instance


class Report(TimeStampedModel):
    cca = models.OneToOneField(
        "assessments.ComplianceCriticalityAssessment",
        verbose_name="Criticality Assessment",
        on_delete=models.CASCADE,
    )
    output_xlsm_1 = models.FileField(
        verbose_name=_("Output XLSM 1"),
        upload_to=upload_report_to,
        **OPTIONAL,
    )
    output_xlsm_2 = models.FileField(
        verbose_name=_("Output XLSM 2"),
        upload_to=upload_report_to,
        **OPTIONAL,
    )
    output_cca_doc = models.FileField(
        verbose_name=_("CCA Document"),
        upload_to=upload_report_to,
        **OPTIONAL,
    )
    compressed_reports = models.FileField(
        verbose_name=_("All Reports"),
        upload_to=upload_report_to,
        help_text=_("This is a zipped file containing all the Report files above."),
        **OPTIONAL,
    )

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")

    def __str__(self):
        date_created_formatted = self.created.strftime("%m/%d/%Y")
        return f"{self.cca.name} Reports - {date_created_formatted}"


class ReviewComment(TimeStampedModel):
    cca = models.ForeignKey(
        "assessments.ComplianceCriticalityAssessment",
        verbose_name=_("Compliance Criticality Assessment"),
        related_name="comments",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "users.User",
        verbose_name=_("Reviewer"),
        related_name="cca_comments",
        on_delete=models.CASCADE,
    )
    comment = models.CharField(verbose_name=_("Comment"), max_length=256)

    class Meta:
        verbose_name = _("Review Comment")
        verbose_name_plural = _("Review Comments")


class AssessmentExport(TimeStampedModel):
    exported_by = models.ForeignKey(
        "users.User",
        verbose_name=_("Exported By"),
        related_name="exports",
        on_delete=models.CASCADE,
    )
    document_file = models.FileField(
        verbose_name=_("Document File"),
        max_length=256,
        upload_to="exports/",
        **OPTIONAL,
    )

    def __str__(self):

        return f"{os.path.basename(self.document_file.file.name)} - {self.exported_by}"

    class Meta:
        verbose_name = _("Assessment Export")
        verbose_name_plural = _("Assessment Exports")
