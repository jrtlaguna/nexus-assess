from datetime import datetime

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.utils import flatten_fieldsets
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from users.admin import CompanyFilter

from . import applogic as assessment_applogic
from .models import (
    AssessmentExport,
    ComplianceCriticalityAssessment,
    Report,
    ReviewComment,
)
from .tasks import create_and_email_export


class ComplianceCriticalityAssessmentAdminForm(forms.ModelForm):
    class Meta:
        model = ComplianceCriticalityAssessment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for user_field in [
            "business_owner",
            "system_owner",
            "it_risk_management_and_compliance",
        ]:
            self.fields[user_field].label_from_instance = (
                lambda user: user.get_display_name()
            )

        if self.instance:
            self.dynamic_fields = [
                ("gxp_impact", assessment_applogic.get_gxp_impact_fields()),
                ("gxp_eres", assessment_applogic.get_gxp_eres_fields()),
                ("sox_impact", assessment_applogic.get_sox_impact_fields()),
                ("privacy_impact", assessment_applogic.get_privacy_impact_fields()),
                (
                    "data_classification",
                    assessment_applogic.get_data_classification_fields(),
                ),
                ("business_impact", assessment_applogic.get_business_impact_fields()),
                ("summary", assessment_applogic.get_summary_fields()),
                ("rating", assessment_applogic.get_rating_fields()),
            ]
            self.generate_dynamic_fields()

            self.fields["approved_by_business_owner"] = forms.NullBooleanField(
                required=False,
                initial=self.instance.approved_by_business_owner,
                widget=forms.Select(
                    choices=[
                        ("", "Not Yet Reviewed"),
                        (True, "Approved"),
                        (False, "Rejected"),
                    ],
                ),
            )
            self.fields["approved_by_system_owner"] = forms.NullBooleanField(
                required=False,
                initial=self.instance.approved_by_system_owner,
                widget=forms.Select(
                    choices=[
                        ("", "Not Yet Reviewed"),
                        (True, "Approved"),
                        (False, "Rejected"),
                    ],
                ),
            )
            self.fields["approved_by_it_risk_management_and_compliance"] = (
                forms.NullBooleanField(
                    required=False,
                    initial=self.instance.approved_by_it_risk_management_and_compliance,
                    widget=forms.Select(
                        choices=[
                            ("", "Not Yet Reviewed"),
                            (True, "Approved"),
                            (False, "Rejected"),
                        ],
                    ),
                )
            )

    def validate_gxp_impact(self, cleaned_data):
        # validate gxp_impact data that it contains all expected keys are boolean
        gxp_impact_data = assessment_applogic.convert_gxp_impact_fields_to_json(
            cleaned_data
        )
        try:
            assessment_applogic.validate_gxp_impact_json(gxp_impact_data)
            cleaned_data["gxp_impact"] = gxp_impact_data

            # we can now remove the individual fields from cleaned_data
            for field in assessment_applogic.get_gxp_impact_fields():
                del cleaned_data[field[0]]

        except forms.ValidationError as e:
            self.add_error(None, e.args[0])

        return cleaned_data

    def validate_gxp_eres(self, cleaned_data):
        # validate gxp_eres data that it contains all expected keys are boolean
        gxp_eres_data = assessment_applogic.convert_gxp_eres_fields_to_json(
            cleaned_data
        )
        try:
            assessment_applogic.validate_gxp_eres_json(gxp_eres_data)
            cleaned_data["gxp_eres"] = gxp_eres_data

            # we can now remove the individual fields from cleaned_data
            for field in assessment_applogic.get_gxp_eres_fields():
                del cleaned_data[field[0]]

        except forms.ValidationError as e:
            self.add_error(None, e.args[0])

        return cleaned_data

    def validate_sox_impact(self, cleaned_data):
        # validate sox_impact data that it contains all expected keys are boolean
        sox_impact_data = assessment_applogic.convert_sox_impact_fields_to_json(
            cleaned_data
        )
        try:
            assessment_applogic.validate_sox_impact_json(sox_impact_data)
            cleaned_data["sox_impact"] = sox_impact_data

            # we can now remove the individual fields from cleaned_data
            for field in assessment_applogic.get_sox_impact_fields():
                del cleaned_data[field[0]]

        except forms.ValidationError as e:
            self.add_error(None, e.args[0])

        return cleaned_data

    def validate_privacy_impact(self, cleaned_data):
        # validate privacy_impact data that it contains all expected keys are boolean
        privacy_impact_data = assessment_applogic.convert_privacy_impact_fields_to_json(
            cleaned_data
        )
        try:
            assessment_applogic.validate_privacy_impact_json(privacy_impact_data)
            cleaned_data["privacy_impact"] = privacy_impact_data

            # we can now remove the individual fields from cleaned_data
            for field in assessment_applogic.get_privacy_impact_fields():
                del cleaned_data[field[0]]

        except forms.ValidationError as e:
            self.add_error(None, e.args[0])

        return cleaned_data

    def validate_data_classification(self, cleaned_data):
        # validate data_classification data that it contains all expected keys are boolean
        data_classification_data = (
            assessment_applogic.convert_data_classification_fields_to_json(cleaned_data)
        )
        try:
            assessment_applogic.validate_data_classification_json(
                data_classification_data
            )
            cleaned_data["data_classification"] = data_classification_data

            # we can now remove the individual fields from cleaned_data
            for field in assessment_applogic.get_data_classification_fields():
                del cleaned_data[field[0]]

        except forms.ValidationError as e:
            self.add_error(None, e.args[0])

        return cleaned_data

    def validate_business_impact(self, cleaned_data):
        # validate business_impact data that it contains all expected keys are boolean
        business_impact_data = (
            assessment_applogic.convert_business_impact_fields_to_json(cleaned_data)
        )
        try:
            assessment_applogic.validate_business_impact_json(business_impact_data)
            cleaned_data["business_impact"] = business_impact_data

            # we can now remove the individual fields from cleaned_data
            for field in assessment_applogic.get_business_impact_fields():
                del cleaned_data[field[0]]

        except forms.ValidationError as e:
            self.add_error(None, e.args[0])

        return cleaned_data

    def validate_approvers(self, cleaned_data):
        # validate that all approvers belong to the same company the CCA form is assigned to
        company = cleaned_data.get("company")
        business_owner = cleaned_data.get("business_owner")
        system_owner = cleaned_data.get("system_owner")
        it_risk_management_and_compliance = cleaned_data.get(
            "it_risk_management_and_compliance"
        )

        if len({business_owner, system_owner, it_risk_management_and_compliance}) != 3:
            self.add_error(None, "Approver for each role should not be the same.")

        if company:
            if not business_owner.company == company:
                self.add_error(
                    "business_owner",
                    "Business Owner should be part of the Company this form is assigned to.",
                )

            if not system_owner.company == company:
                self.add_error(
                    "system_owner",
                    "System Owner should be part of the Company this form is assigned to.",
                )

            if not it_risk_management_and_compliance.company == company:
                self.add_error(
                    "it_risk_management_and_compliance",
                    "IT Risk Management and Compliance should be part of the Company this form is assigned to.",
                )

        return cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        solution_type = cleaned_data.get("solution_type")
        other_solution_type = cleaned_data.get("other_solution_type")

        if (
            solution_type
            and solution_type == ComplianceCriticalityAssessment.SolutionType.OTHER
        ):
            if not other_solution_type:
                self.add_error(
                    "other_solution_type",
                    forms.ValidationError(
                        "This field is required if Solution Type is set to 'Other'."
                    ),
                )
        elif (
            solution_type
            and solution_type != ComplianceCriticalityAssessment.SolutionType.OTHER
            and other_solution_type
        ):
            # if solution type is not Other and a value was provided for other_solution_type,
            # ignore the value
            cleaned_data["other_solution_type"] = ""

        # validate the dynamic fields
        cleaned_data = self.validate_gxp_impact(cleaned_data)
        cleaned_data = self.validate_gxp_eres(cleaned_data)
        cleaned_data = self.validate_sox_impact(cleaned_data)
        cleaned_data = self.validate_privacy_impact(cleaned_data)
        cleaned_data = self.validate_data_classification(cleaned_data)
        cleaned_data = self.validate_business_impact(cleaned_data)

        # shared validations
        gxp_impact = cleaned_data.get("gxp_impact")
        gxp_impact_boolean = [
            key for key in gxp_impact.keys() if not key.endswith("_comment")
        ]
        gxp_eres = cleaned_data.get("gxp_eres")
        gxp_eres_boolean = [
            key for key in gxp_eres.keys() if not key.endswith("_comment")
        ]

        # Validation/Enforce logic: If all boolean fields in gxp_impact are False, set all boolean fields in gxp_eres to False
        if all(
            value is False
            for key, value in gxp_impact.items()
            if key in gxp_impact_boolean
        ):
            for key in gxp_eres_boolean:
                gxp_eres[key] = False

        # validate approvers
        cleaned_data = self.validate_approvers(cleaned_data)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.id:
            instance.gxp_impact = self.cleaned_data.get(
                "gxp_impact", instance.gxp_impact
            )
            instance.gxp_eres = self.cleaned_data.get("gxp_eres", instance.gxp_eres)
            instance.sox_impact = self.cleaned_data.get(
                "sox_impact", instance.sox_impact
            )
            instance.privacy_impact = self.cleaned_data.get(
                "privacy_impact", instance.privacy_impact
            )
            instance.data_classification = self.cleaned_data.get(
                "data_classification", instance.data_classification
            )
            instance.business_impact = self.cleaned_data.get(
                "business_impact", instance.business_impact
            )
            instance.approved_by_business_owner = self.cleaned_data[
                "approved_by_business_owner"
            ]
            if self.cleaned_data["approved_by_business_owner"]:
                instance.datetime_approved_by_business_owner = datetime.now()
            instance.approved_by_system_owner = self.cleaned_data[
                "approved_by_system_owner"
            ]
            if self.cleaned_data["approved_by_system_owner"]:
                instance.datetime_approved_by_system_owner = datetime.now()
            instance.approved_by_it_risk_management_and_compliance = self.cleaned_data[
                "approved_by_it_risk_management_and_compliance"
            ]
            if self.cleaned_data["approved_by_it_risk_management_and_compliance"]:
                instance.datetime_approved_by_it_risk_management_and_compliance = (
                    datetime.now()
                )
        else:
            instance.drafted_by = self.user

        if commit:
            instance.save()

        return instance

    def generate_dynamic_fields(self):
        for field_group_pair in self.dynamic_fields:
            field_name = field_group_pair[0]
            field_group = field_group_pair[1]

            for field in field_group:
                if field[0].endswith("_comment"):
                    initial_value = ""
                    if self.instance:
                        initial_value = getattr(self.instance, field_name).get(
                            field[0], ""
                        )

                    self.fields.update(
                        {
                            field[0]: forms.CharField(
                                widget=forms.Textarea(
                                    attrs={"rows": 4, "style": "resize: both;"}
                                ),
                                required=False,
                                label=field[1],
                                initial=initial_value,
                            )
                        }
                    )
                else:
                    initial_value = False
                    if self.instance:
                        initial_value = getattr(self.instance, field_name).get(
                            field[0], False
                        )
                    if field_name in [
                        "summary",
                        "rating",
                        "business_impact",
                        "data_classification",
                    ]:
                        boolean_field = forms.BooleanField(
                            required=False,
                            label=field[1],
                            initial=initial_value,
                            label_suffix="",
                        )
                    else:
                        boolean_field = forms.NullBooleanField(
                            widget=forms.Select(
                                choices=[
                                    ("", "Unanswered"),
                                    (True, "Yes"),
                                    (False, "No"),
                                ],
                                attrs={"class": "null-boolean-select"},
                            ),
                            required=False,
                            label=field[1],
                            initial=initial_value,
                            label_suffix="",
                        )
                    self.fields.update({field[0]: boolean_field})

        # set summary and rating fields to be readonly
        readonly_dynamic_fields = [
            assessment_applogic.get_summary_fields(),
            assessment_applogic.get_rating_fields(),
        ]

        for field_group in readonly_dynamic_fields:
            for field in field_group:
                if not field[0] == "rating_comment":
                    self.fields[field[0]].widget.attrs["disabled"] = "disabled"


@admin.register(ComplianceCriticalityAssessment)
class ComplianceCritcalityAssessmentAdmin(admin.ModelAdmin):
    form = ComplianceCriticalityAssessmentAdminForm
    change_list_template = "admin/assessment_change_list.html"
    add_fieldsets = (
        (
            None,
            {
                "fields": [
                    "company",
                ]
            },
        ),
        (
            "Approvers",
            {
                "fields": [
                    "business_owner",
                    "system_owner",
                    "it_risk_management_and_compliance",
                ]
            },
        ),
        (
            "Solution Identification",
            {
                "fields": [
                    "solution_name",
                    "solution_version",
                    "vendor_name",
                    "solution_type",
                    "other_solution_type",
                    "hosting_and_type",
                    "server_host",
                    "solution_classification",
                ]
            },
        ),
    )
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "created",
                    "drafted_by",
                    "company",
                ]
            },
        ),
        (
            "Approvers",
            {
                "fields": [
                    "business_owner",
                    "system_owner",
                    "it_risk_management_and_compliance",
                ]
            },
        ),
        (
            "Status",
            {
                "fields": [
                    "status",
                    "approved_by_business_owner",
                    "datetime_approved_by_business_owner",
                    "approved_by_system_owner",
                    "datetime_approved_by_system_owner",
                    "approved_by_it_risk_management_and_compliance",
                    "datetime_approved_by_it_risk_management_and_compliance",
                ],
                "classes": ["cca_status"],
            },
        ),
        (
            "Solution Identification",
            {
                "fields": [
                    "solution_name",
                    "solution_version",
                    "vendor_name",
                    "solution_type",
                    "other_solution_type",
                    "hosting_and_type",
                    "server_host",
                    "solution_classification",
                ]
            },
        ),
        (
            "Description and Intended Use",
            {
                "fields": [
                    "solution_description",
                ],
                "classes": [
                    "collapse",
                ],
            },
        ),
    ]
    list_display = [
        "name",
        "company",
        "solution_name",
        "vendor_name",
        "solution_type",
        "hosting_and_type",
        "server_host",
        "solution_classification",
        "status",
    ]
    readonly_fields = [
        "created",
        "drafted_by",
        "status",
        # "approved_by_business_owner",
        "datetime_approved_by_business_owner",
        # "approved_by_system_owner",
        "datetime_approved_by_system_owner",
        # "approved_by_it_risk_management_and_compliance",
        "datetime_approved_by_it_risk_management_and_compliance",
    ]
    search_fields = ["id", "solution_name", "vendor_name", "server_host"]
    list_filter = [
        "status",
        CompanyFilter,
        "solution_type",
        "hosting_and_type",
        "solution_classification",
    ]
    ordering = ["-id"]
    autocomplete_fields = [
        "company",
        "business_owner",
        "system_owner",
        "it_risk_management_and_compliance",
    ]

    class Media:
        css = {
            "all": ("css/admin/custom.css",),
        }

    def get_form(self, request, obj=None, **kwargs):
        # we'll use add_fieldsets here since this one does not have the dynamic fields
        # adding the dynamic fields to the fieldset makes django expect that those fields inherently
        # exists in the modelform, causes key error issues on fields
        fields = flatten_fieldsets(self.add_fieldsets)
        fields.append("solution_description")
        kwargs["fields"] = fields

        form = super().get_form(request, obj, **kwargs)
        form.user = request.user
        return form

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        fieldsets = self.fieldsets

        # Add the GXP Impact fieldset
        gxp_impact_fieldset = (
            "GXP Impact",
            {
                "fields": [
                    field[0] for field in assessment_applogic.get_gxp_impact_fields()
                ],
                "classes": ["collapse", "cca_questionnaire"],
            },
        )
        if gxp_impact_fieldset not in fieldsets:
            fieldsets.append(gxp_impact_fieldset)

        # Add the GXP ERES fieldset
        gxp_eres_fieldset = (
            "GxP Electronic Records (ER) and Electronic Signatures (ES) Applicability",
            {
                "fields": [
                    field[0] for field in assessment_applogic.get_gxp_eres_fields()
                ],
                "classes": ["collapse", "cca_questionnaire"],
                "description": _(
                    "Below questions are applicable to GxP solutions only. Keep the options unchecked if the solution is non-GxP."
                ),
            },
        )
        if gxp_eres_fieldset not in fieldsets:
            fieldsets.append(gxp_eres_fieldset)

        # Add the SOX Impact fieldset
        sox_impact_fieldset = (
            "SOX Impact",
            {
                "fields": [
                    field[0] for field in assessment_applogic.get_sox_impact_fields()
                ],
                "classes": ["collapse", "cca_questionnaire"],
            },
        )
        if sox_impact_fieldset not in fieldsets:
            fieldsets.append(sox_impact_fieldset)

        # Add the Privacy Impact fieldset
        privacy_impact_fieldset = (
            "Privacy Impact",
            {
                "fields": [
                    field[0]
                    for field in assessment_applogic.get_privacy_impact_fields()
                ],
                "classes": ["collapse", "cca_questionnaire"],
            },
        )
        if privacy_impact_fieldset not in fieldsets:
            fieldsets.append(privacy_impact_fieldset)

        # Add the Data Classification fieldset
        data_classification_fieldset = (
            "Data Classification",
            {
                "fields": [
                    field[0]
                    for field in assessment_applogic.get_data_classification_fields()
                ],
                "classes": ["collapse", "cca_questionnaire"],
            },
        )
        if data_classification_fieldset not in fieldsets:
            fieldsets.append(data_classification_fieldset)

        # Add the Business Impact fieldset
        business_impact_fieldset = (
            "Business Impact",
            {
                "fields": [
                    field[0]
                    for field in assessment_applogic.get_business_impact_fields()
                ],
                "classes": ["collapse", "cca_questionnaire"],
            },
        )
        if business_impact_fieldset not in fieldsets:
            fieldsets.append(business_impact_fieldset)

        # Add the Summary fieldset
        summary_fieldset = (
            "Solution Criticality Summary",
            {
                "fields": [
                    tuple(item[0] for item in subgroup)
                    for subgroup in assessment_applogic.get_summary_fields(grouped=True)
                ],
                "classes": ["collapse", "summary-fields"],
                "description": _(
                    "The fields below will automatically be filled out everytime the form is updated based on the responses in the above question."
                ),
            },
        )

        if summary_fieldset not in fieldsets:
            fieldsets.append(summary_fieldset)

        # Add the Rating fieldset
        summary_fieldset = (
            "Compliance Criticality Rating",
            {
                "fields": [
                    field[0] for field in assessment_applogic.get_rating_fields()
                ],
                "classes": ["collapse", "cca_questionnaire"],
                "description": _(
                    "The fields below will automatically be filled out everytime the form is updated based on the responses in the above question."
                ),
            },
        )
        if summary_fieldset not in fieldsets:
            fieldsets.append(summary_fieldset)

        return fieldsets

    def get_solution_type(self, obj):
        return obj.solution_type_display

    get_solution_type.short_description = "Solution Type"

    @admin.action(description=_("Export Selected Assessments"))
    def export_all_assessments(self, request, queryset):
        create_and_email_export.delay(
            list(queryset.values_list("id", flat=True)), request.user.id
        )
        messages.info(
            request,
            _(
                "Exporting assessments document. Download link will be sent to your email shortly."
            ),
        )

    @admin.action(description=_("Re-generate Reports for selected Assessments"))
    def regenerate_reports(self, request, queryset):
        if queryset.filter(
            ~Q(status=ComplianceCriticalityAssessment.Status.APPROVED)
        ).exists():
            messages.error(
                request,
                _(
                    "There are Unapproved forms in the selection. Please generate reports with an Approved status only."
                ),
            )
        else:
            for cca in queryset:
                cca.run_generate_reports_chain()

            messages.info(
                request,
                _(
                    "Re-generating Reports in the background. You can come back in a while to check."
                ),
            )

    actions = [export_all_assessments, regenerate_reports]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ["cca"]}),
        (
            "Files",
            {
                "fields": [
                    "output_xlsm_1",
                    "output_xlsm_2",
                    "output_cca_doc",
                    "compressed_reports",
                ]
            },
        ),
        (None, {"fields": ["get_last_modified"]}),
    )
    search_fields = ["cca__name", "cca__company__name"]
    list_display = ["cca", "get_company_name", "created", "modified"]
    readonly_fields = [
        "cca",
        "output_xlsm_1",
        "output_xlsm_2",
        "output_cca_doc",
        "compressed_reports",
        "get_last_modified",
    ]
    ordering = ["-cca__id"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_company_name(self, obj):
        if hasattr(obj.cca, "company"):
            return obj.cca.company.name
        return ""

    get_company_name.short_description = "Company"

    def get_last_modified(self, obj):
        return obj.modified.strftime("%b. %d, %Y, %I:%M %p")

    get_last_modified.short_description = "Last updated"


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = ["id", "cca", "user", "comment", "created"]
    search_fields = ["cca_id"]


@admin.register(AssessmentExport)
class AssessmentExportAdmin(admin.ModelAdmin):
    search_fields = [
        "exported_by__first_name",
        "exported_by__last_name",
        "exported_by__email",
    ]
    list_display = ["__str__", "exported_by"]
    readonly_fields = ["exported_by", "document_file"]
