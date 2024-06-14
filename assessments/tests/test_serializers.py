from datetime import datetime

import pytest
from freezegun import freeze_time
from rest_framework import serializers

from django.contrib.auth import get_user_model

from users.tests.factories import CompanyFactory, UserFactory

from ..api.v1.serializers import (
    ComplianceCriticalityAssessmentListSerializer,
    ComplianceCriticalityAssessmentSummarySerializer,
    ReviewCommentSerializer,
)
from ..applogic import (
    business_impact_applogic,
    data_classification_applogic,
    gxp_eres_applogic,
    gxp_impact_applogic,
    privacy_impact_applogic,
    sox_impact_applogic,
)
from ..models import ComplianceCriticalityAssessment, ReviewComment
from .factories import ComplianceCriticalityAssessmentFactory, ReviewCommentFactory


@pytest.mark.django_db
def test_review_comment_serializer():
    review_comment = ReviewCommentFactory()
    serializer = ReviewCommentSerializer(instance=review_comment)
    data = serializer.data

    assert data["id"] == review_comment.id
    assert data["comment"] == review_comment.comment
    # Add more assertions based on your model fields


@freeze_time("2022-01-01 12:00:00")
@pytest.mark.django_db
def test_compliance_assessment_list_serializer():
    assessment = ComplianceCriticalityAssessmentFactory()
    serializer = ComplianceCriticalityAssessmentListSerializer(instance=assessment)

    expected_keys = [
        "id",
        "name",
        "company",
        "drafted_by",
        "business_owner",
        "system_owner",
        "it_risk_management_and_compliance",
        "created",
        "modified",
        "status",
        "approved_by_business_owner",
        "datetime_approved_by_business_owner",
        "approved_by_system_owner",
        "datetime_approved_by_system_owner",
        "approved_by_it_risk_management_and_compliance",
        "datetime_approved_by_it_risk_management_and_compliance",
        "solution_name",
        "solution_version",
        "vendor_name",
        "solution_type",
        "other_solution_type",
        "hosting_and_type",
        "server_host",
        "solution_classification",
        "latest_comments",
    ]
    result_keys = serializer.data.keys()
    assert set(expected_keys) == set(result_keys)

    assert "id" in serializer.data["company"]
    assert "id" in serializer.data["drafted_by"]
    assert "id" in serializer.data["business_owner"]
    assert "id" in serializer.data["system_owner"]
    assert "id" in serializer.data["it_risk_management_and_compliance"]
    assert isinstance(serializer.data["latest_comments"], list)


@pytest.mark.django_db
def test_latest_comments_method():
    business_owner = UserFactory()
    system_owner = UserFactory()
    it_risk_management_and_compliance = UserFactory()
    assessment = ComplianceCriticalityAssessmentFactory(
        business_owner=business_owner,
        system_owner=system_owner,
        it_risk_management_and_compliance=it_risk_management_and_compliance,
    )

    business_owner_comment = ReviewCommentFactory(cca=assessment, user=business_owner)
    system_owner_comment = ReviewCommentFactory(cca=assessment, user=system_owner)
    it_risk_management_and_compliance_comment = ReviewCommentFactory(
        cca=assessment,
        user=it_risk_management_and_compliance,
    )

    # create a newer comment, should now be returned instead of the old one
    business_owner_comment2 = ReviewCommentFactory(cca=assessment, user=business_owner)

    serializer = ComplianceCriticalityAssessmentListSerializer(instance=assessment)

    assert len(serializer.data["latest_comments"]) == 3
    assert business_owner_comment2.id == serializer.data["latest_comments"][0]["id"]
    assert system_owner_comment.id == serializer.data["latest_comments"][1]["id"]
    assert (
        it_risk_management_and_compliance_comment.id
        == serializer.data["latest_comments"][2]["id"]
    )


def test_summary_and_rating_serializer_valid_data():
    valid_data = {
        "gxp_impact": gxp_impact_applogic.get_default_gxp_impact_json_value(),
        "gxp_eres": gxp_eres_applogic.get_default_gxp_eres_json_value(),
        "sox_impact": sox_impact_applogic.get_default_sox_impact_json_value(),
        "privacy_impact": privacy_impact_applogic.get_default_privacy_impact_json_value(),
        "data_classification": data_classification_applogic.get_default_data_classification_json_value(),
        "business_impact": business_impact_applogic.get_default_business_impact_json_value(),
    }

    serializer = ComplianceCriticalityAssessmentSummarySerializer(data=valid_data)
    assert serializer.is_valid()


def test_summary_and_rating_serializer_invalid_data():
    invalid_data = {
        "gxp_impact": {"invalid_key": "value"},
        "gxp_eres": {"key": "value"},
        "sox_impact": {"key": "value"},
        "privacy_impact": {"key": "value"},
        "data_classification": {"key": "value"},
        "business_impact": {"key": "value"},
    }

    serializer = ComplianceCriticalityAssessmentSummarySerializer(data=invalid_data)
    assert not serializer.is_valid()
