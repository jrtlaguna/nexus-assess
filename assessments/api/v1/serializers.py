from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from users.api.v1.serializers import BaseUserSerializer, CompanySerializer

from ...models import ComplianceCriticalityAssessment, Report, ReviewComment


class ReviewCommentSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer(read_only=True)

    class Meta:
        model = ReviewComment
        fields = [
            "id",
            "created",
            "comment",
            "user",
        ]


class ReviewCommentInputSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False)


class ComplianceCriticalityAssessmentSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    drafted_by = BaseUserSerializer(read_only=True)
    business_owner = BaseUserSerializer(read_only=True)
    system_owner = BaseUserSerializer(read_only=True)
    it_risk_management_and_compliance = BaseUserSerializer(read_only=True)
    comments = ReviewCommentSerializer(many=True, required=False)
    report_url = serializers.SerializerMethodField()
    latest_comments = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        if user := self.context.get("user"):
            instance.drafted_by = user
            instance.save(update_fields=["drafted_by"])
        return super().update(instance, validated_data)

    class Meta:
        model = ComplianceCriticalityAssessment
        fields = "__all__"
        read_only_fields = (
            # should only be editable via applogic, no direct modification from API
            "status",
            "approved_by_business_owner",
            "approved_by_system_owner",
            "approved_by_it_risk_management_and_compliance",
            # should only be editable through admin site
            "solution_name",
            "solution_version",
            "vendor_name",
            "solution_type",
            "other_solution_type",
            "server_host",
            "solution_classification",
            "comments",
            "latest_comments",
        )

    def get_report_url(self, obj):
        if hasattr(obj, "report"):
            if obj.report.compressed_reports:
                return obj.report.compressed_reports.url
        return ""

    def get_latest_comments(self, obj):
        business_owner_comment = (
            obj.comments.filter(user=obj.business_owner).order_by("-created").first()
        )
        system_owner_comment = (
            obj.comments.filter(user=obj.system_owner).order_by("-created").first()
        )
        it_risk_management_and_compliance_comment = (
            obj.comments.filter(user=obj.it_risk_management_and_compliance)
            .order_by("-created")
            .first()
        )

        comments = []
        if business_owner_comment:
            comments.append(business_owner_comment)
        if system_owner_comment:
            comments.append(system_owner_comment)
        if it_risk_management_and_compliance_comment:
            comments.append(it_risk_management_and_compliance_comment)

        serializer = ReviewCommentSerializer(comments, many=True)
        return serializer.data


class ComplianceCriticalityAssessmentListSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    drafted_by = BaseUserSerializer(read_only=True)
    business_owner = BaseUserSerializer(read_only=True)
    system_owner = BaseUserSerializer(read_only=True)
    it_risk_management_and_compliance = BaseUserSerializer(read_only=True)
    latest_comments = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceCriticalityAssessment
        exclude = [
            "solution_description",
            "gxp_impact",
            "gxp_eres",
            "sox_impact",
            "privacy_impact",
            "data_classification",
            "business_impact",
            "summary",
            "rating",
        ]
        read_only_fields = (
            # should only be editable via applogic, no direct modification from API
            "status",
            "approved_by_business_owner",
            "approved_by_system_owner",
            "approved_by_it_risk_management_and_compliance",
            # should only be editable through admin site
            "solution_name",
            "solution_version",
            "vendor_name",
            "solution_type",
            "other_solution_type",
            "server_host",
            "solution_classification",
            # custom fields
            "latest_comments",
        )

    def get_latest_comments(self, obj):
        business_owner_comment = (
            obj.comments.filter(user=obj.business_owner).order_by("-created").first()
        )
        system_owner_comment = (
            obj.comments.filter(user=obj.system_owner).order_by("-created").first()
        )
        it_risk_management_and_compliance_comment = (
            obj.comments.filter(user=obj.it_risk_management_and_compliance)
            .order_by("-created")
            .first()
        )

        comments = []
        if business_owner_comment:
            comments.append(business_owner_comment)
        if system_owner_comment:
            comments.append(system_owner_comment)
        if it_risk_management_and_compliance_comment:
            comments.append(it_risk_management_and_compliance_comment)

        serializer = ReviewCommentSerializer(comments, many=True)
        return serializer.data


class ComplianceCriticalityAssessmentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceCriticalityAssessment
        fields = [
            "gxp_impact",
            "gxp_eres",
            "sox_impact",
            "privacy_impact",
            "data_classification",
            "business_impact",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].required = True

    def validate(self, data):
        gxp_impact = data.get("gxp_impact", {})
        gxp_impact_boolean = [
            key for key in gxp_impact.keys() if not key.endswith("_comment")
        ]

        gxp_eres = data.get("gxp_eres", {})
        gxp_eres_boolean = [
            key for key in gxp_eres.keys() if not key.endswith("_comment")
        ]

        # Validation: If all boolean fields in gxp_impact are False, set all boolean fields in gxp_eres to False
        if all(
            value is False
            for key, value in gxp_impact.items()
            if key in gxp_impact_boolean
        ):
            for key in gxp_eres_boolean:
                gxp_eres[key] = False

        return data
