import json
from unittest.mock import Mock, patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.urls import reverse

from users.tests.factories import CompanyFactory, UserFactory

from ..api.v1.serializers import ComplianceCriticalityAssessmentListSerializer
from ..api.v1.views import CcaApiModelViewset, CCASearchFilter
from ..applogic import (
    business_impact_applogic,
    data_classification_applogic,
    gxp_eres_applogic,
    gxp_impact_applogic,
    privacy_impact_applogic,
    rating_applogic,
    sox_impact_applogic,
    summary_applogic,
)
from ..models import ComplianceCriticalityAssessment, ReviewComment
from .factories import ComplianceCriticalityAssessmentFactory, ReviewCommentFactory

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_user(api_client):
    user = UserFactory(company=CompanyFactory())

    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def authenticated_user_with_no_company(api_client):
    user = UserFactory()

    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.mark.django_db
def test_get_list(authenticated_user):
    api_client, user = authenticated_user

    other_company = CompanyFactory(name="Other company")

    cca1 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 1", company=user.company
    )
    cca2 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 2", company=user.company
    )
    cca3 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 3", company=other_company
    )

    url = reverse("v1:cca-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    data = json.loads(response.content)
    expected_keys = ["count", "next", "previous", "results"]
    data_ids = [item["id"] for item in data["results"]]

    assert set(data.keys()) == set(expected_keys)
    assert data_ids == [cca2.id, cca1.id]
    assert cca3.id not in data_ids


@pytest.mark.django_db
def test_filter_by_status(authenticated_user):
    api_client, user = authenticated_user

    other_company = CompanyFactory(name="Other company")

    cca1 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 1",
        company=user.company,
        status=ComplianceCriticalityAssessment.Status.DRAFT,
    )
    cca2 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 2",
        company=user.company,
        status=ComplianceCriticalityAssessment.Status.FOR_REVIEW,
    )
    cca3 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 3",
        company=other_company,
        status=ComplianceCriticalityAssessment.Status.DRAFT,
    )

    url = reverse("v1:cca-list")
    response = api_client.get(
        url, {"status": ComplianceCriticalityAssessment.Status.DRAFT}
    )

    assert response.status_code == status.HTTP_200_OK

    data = json.loads(response.content)
    data_ids = [item["id"] for item in data["results"]]

    assert data_ids == [cca1.id]

    # check multiple values
    status_data = ",".join(
        [
            ComplianceCriticalityAssessment.Status.DRAFT,
            ComplianceCriticalityAssessment.Status.FOR_REVIEW,
        ]
    )
    response = api_client.get(url, {"status": status_data})

    assert response.status_code == status.HTTP_200_OK

    data = json.loads(response.content)
    data_ids = [item["id"] for item in data["results"]]

    assert data_ids == [cca2.id, cca1.id]


@pytest.mark.django_db
def test_filter_by_solution_type(authenticated_user):
    api_client, user = authenticated_user

    other_company = CompanyFactory(name="Other company")

    cca1 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 1",
        company=user.company,
        solution_type=ComplianceCriticalityAssessment.SolutionType.APPLICATION,
    )
    cca2 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 2",
        company=user.company,
        solution_type=ComplianceCriticalityAssessment.SolutionType.INFRASTRUCTURE,
    )
    cca3 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 3",
        company=other_company,
        solution_type=ComplianceCriticalityAssessment.SolutionType.MIDDLEWARE,
    )

    url = reverse("v1:cca-list")
    response = api_client.get(
        url, {"solution_type": ComplianceCriticalityAssessment.SolutionType.APPLICATION}
    )

    assert response.status_code == status.HTTP_200_OK

    data = json.loads(response.content)
    data_ids = [item["id"] for item in data["results"]]

    assert data_ids == [cca1.id]

    # check multiple values
    solution_type = ",".join(
        [
            ComplianceCriticalityAssessment.SolutionType.APPLICATION,
            ComplianceCriticalityAssessment.SolutionType.INFRASTRUCTURE,
        ]
    )
    response = api_client.get(url, {"solution_type": solution_type})

    assert response.status_code == status.HTTP_200_OK

    data = json.loads(response.content)
    data_ids = [item["id"] for item in data["results"]]

    assert data_ids == [cca2.id, cca1.id]


@pytest.mark.django_db
def test_filter_by_solution_classification(authenticated_user):
    api_client, user = authenticated_user

    other_company = CompanyFactory(name="Other company")

    cca1 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 1",
        company=user.company,
        solution_classification=ComplianceCriticalityAssessment.SolutionClassification.CONFIGURABLE,
    )
    cca2 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 2",
        company=user.company,
        solution_classification=ComplianceCriticalityAssessment.SolutionClassification.NON_CONFIGURABLE,
    )
    cca3 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 3",
        company=other_company,
        solution_classification=ComplianceCriticalityAssessment.SolutionClassification.CUSTOM,
    )

    url = reverse("v1:cca-list")
    response = api_client.get(
        url,
        {
            "solution_classification": ComplianceCriticalityAssessment.SolutionClassification.CONFIGURABLE
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = json.loads(response.content)
    data_ids = [item["id"] for item in data["results"]]

    assert data_ids == [cca1.id]

    # check multiple values
    solution_classification = ",".join(
        [
            ComplianceCriticalityAssessment.SolutionClassification.CONFIGURABLE,
            ComplianceCriticalityAssessment.SolutionClassification.NON_CONFIGURABLE,
        ]
    )
    response = api_client.get(url, {"solution_classification": solution_classification})

    assert response.status_code == status.HTTP_200_OK

    data = json.loads(response.content)
    data_ids = [item["id"] for item in data["results"]]

    assert data_ids == [cca2.id, cca1.id]


@pytest.mark.django_db
def test_filter_by_hosting_and_type(authenticated_user):
    api_client, user = authenticated_user

    other_company = CompanyFactory(name="Other company")

    cca1 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 1",
        company=user.company,
        hosting_and_type=ComplianceCriticalityAssessment.HostingAndType.IAAS,
    )
    cca2 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 2",
        company=user.company,
        hosting_and_type=ComplianceCriticalityAssessment.HostingAndType.ON_PREMISES,
    )
    cca3 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 3",
        company=other_company,
        hosting_and_type=ComplianceCriticalityAssessment.HostingAndType.PAAS,
    )

    url = reverse("v1:cca-list")
    response = api_client.get(
        url, {"hosting_and_type": ComplianceCriticalityAssessment.HostingAndType.IAAS}
    )

    assert response.status_code == status.HTTP_200_OK

    data = json.loads(response.content)
    data_ids = [item["id"] for item in data["results"]]

    assert data_ids == [cca1.id]

    # check multiple values
    hosting_and_type = ",".join(
        [
            ComplianceCriticalityAssessment.HostingAndType.IAAS,
            ComplianceCriticalityAssessment.HostingAndType.ON_PREMISES,
        ]
    )
    response = api_client.get(url, {"hosting_and_type": hosting_and_type})

    assert response.status_code == status.HTTP_200_OK

    data = json.loads(response.content)
    data_ids = [item["id"] for item in data["results"]]

    assert data_ids == [cca2.id, cca1.id]


@pytest.mark.django_db
def test_get_list_when_user_has_no_company(authenticated_user_with_no_company):
    api_client, user = authenticated_user_with_no_company

    cca1 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 1",
        company=user.company,
        status=ComplianceCriticalityAssessment.Status.DRAFT,
    )
    cca2 = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 2",
        company=user.company,
        status=ComplianceCriticalityAssessment.Status.FOR_REVIEW,
    )

    url = reverse("v1:cca-list")
    response = api_client.get(
        url, {"status": ComplianceCriticalityAssessment.Status.DRAFT}
    )

    assert response.status_code == status.HTTP_200_OK

    data = json.loads(response.content)
    data_ids = [item["id"] for item in data["results"]]

    assert data_ids == []


@pytest.mark.django_db
def test_filter_queryset():
    filter_instance = CCASearchFilter()

    # Mock get_search_fields and get_search_terms
    with patch.object(
        filter_instance,
        "get_search_fields",
        return_value=CcaApiModelViewset.search_fields,
    ):
        with patch.object(
            filter_instance, "get_search_terms", return_value=["Form", "#1"]
        ):
            cca1 = ComplianceCriticalityAssessmentFactory(name="Form #1")
            cca2 = ComplianceCriticalityAssessmentFactory(name="Form #2")

            queryset = ComplianceCriticalityAssessment.objects.all()
            mock_request = Mock(
                spec=RequestFactory().get(
                    "/your-api-endpoint/", {"search": "search_term"}
                )
            )

            filtered_queryset = filter_instance.filter_queryset(
                mock_request, queryset, None
            )

    assert filtered_queryset.count() == 1
    assert cca1.id in filtered_queryset.values_list("id", flat=True)
    assert not cca2.id in filtered_queryset.values_list("id", flat=True)


@pytest.mark.django_db
def test_cca_summary_and_rating_view(authenticated_user):
    api_client, user = authenticated_user

    data = {
        "gxp_impact": gxp_impact_applogic.get_default_gxp_impact_json_value(),
        "gxp_eres": gxp_eres_applogic.get_default_gxp_eres_json_value(),
        "sox_impact": sox_impact_applogic.get_default_sox_impact_json_value(),
        "privacy_impact": privacy_impact_applogic.get_default_privacy_impact_json_value(),
        "data_classification": data_classification_applogic.get_default_data_classification_json_value(),
        "business_impact": business_impact_applogic.get_default_business_impact_json_value(),
    }

    url = reverse("v1:cca-summary")
    response = api_client.post(
        url, data=json.dumps(data), content_type="application/json"
    )

    # Assert the response status code
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "summary" in response.data
    assert "rating" in response.data

    summary = summary_applogic.calculate_summary(data)
    rating = rating_applogic.calculate_rating(summary)
    assert response.data["summary"] == summary
    assert response.data["rating"] == rating

    # test bad request
    url = reverse("v1:cca-summary")
    response = api_client.post(
        url,
        data=json.dumps({"invalid_key": "invalid_data"}),
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_retrieve_compliance_criticality_assessment(authenticated_user):
    api_client, user = authenticated_user

    user2 = UserFactory()
    cca = ComplianceCriticalityAssessmentFactory(company=user.company)
    cca2 = ComplianceCriticalityAssessmentFactory(company=user2.company)

    # get owned cca
    url = reverse("v1:cca-detail", args=[cca.pk])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "data" in response.json()
    data = response.json()["data"]
    assert data["id"] == cca.id

    # get un-owned cca
    url = reverse("v1:cca-detail", args=[cca2.pk])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_comments_action(authenticated_user):
    api_client, user = authenticated_user

    user2 = UserFactory()
    cca = ComplianceCriticalityAssessmentFactory(company=user.company)
    cca2 = ComplianceCriticalityAssessmentFactory(company=user2.company)
    comment1 = ReviewCommentFactory(cca=cca)
    comment2 = ReviewCommentFactory(cca=cca)
    comment3 = ReviewCommentFactory(cca=cca2)

    url = reverse("v1:cca-comments", args=[cca.pk])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "data" in response.json()
    data = response.json()["data"]
    assert len(data) == 2
    expected_ids = [comment1.id, comment2.id]
    assert set([item["id"] for item in data]) == set(expected_ids)


@pytest.mark.django_db
def test_approve_cca_action(authenticated_user, *args):
    api_client, user = authenticated_user

    business_owner = UserFactory(company=user.company)
    system_owner = UserFactory(company=user.company)
    compliance_officer = UserFactory(company=user.company)

    cca = ComplianceCriticalityAssessmentFactory(
        status=ComplianceCriticalityAssessment.Status.FOR_REVIEW,
        company=user.company,
        business_owner=business_owner,
        system_owner=system_owner,
        it_risk_management_and_compliance=compliance_officer,
    )

    url = reverse("v1:cca-approve-cca", args=[cca.pk])

    with patch(
        "assessments.models.ComplianceCriticalityAssessment.run_generate_reports_chain"
    ):
        # approve as the drafter
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # approve as businees_owner
        api_client.force_authenticate(user=business_owner)
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "success" in response.json()
        cca.refresh_from_db()
        assert cca.status == ComplianceCriticalityAssessment.Status.FOR_REVIEW
        assert cca.approved_by_business_owner
        assert not cca.approved_by_system_owner
        assert not cca.approved_by_it_risk_management_and_compliance

        # approve as system_owner
        api_client.force_authenticate(user=system_owner)
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "success" in response.json()
        cca.refresh_from_db()
        assert cca.status == ComplianceCriticalityAssessment.Status.FOR_REVIEW
        assert cca.approved_by_business_owner
        assert cca.approved_by_system_owner
        assert not cca.approved_by_it_risk_management_and_compliance

        # approve as compliance_officer
        api_client.force_authenticate(user=compliance_officer)
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "success" in response.json()
        cca.refresh_from_db()
        assert cca.status == ComplianceCriticalityAssessment.Status.APPROVED
        assert cca.approved_by_business_owner
        assert cca.approved_by_system_owner
        assert cca.approved_by_it_risk_management_and_compliance


@pytest.mark.django_db
def test_reject_cca_action(authenticated_user):
    api_client, user = authenticated_user

    cca = ComplianceCriticalityAssessmentFactory(
        status=ComplianceCriticalityAssessment.Status.FOR_REVIEW,
        company=user.company,
        business_owner=user,
    )

    url = reverse("v1:cca-reject-cca", args=[cca.pk])
    data = {"comment": "Test rejection comment"}

    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "data" in response.json()

    cca.refresh_from_db()
    comment = ReviewComment.objects.filter(user=user)

    assert comment.count() == 1
    assert comment.first().comment == data["comment"]
    assert comment.first().user == user
    assert comment.first().cca == cca
    assert cca.status == ComplianceCriticalityAssessment.Status.FOR_REVIEW


@pytest.mark.django_db
def test_reject_cca_action_with_transition(authenticated_user):
    api_client, user = authenticated_user

    cca = ComplianceCriticalityAssessmentFactory(
        status=ComplianceCriticalityAssessment.Status.FOR_REVIEW,
        company=user.company,
        approved_by_business_owner=True,
        approved_by_system_owner=True,
        it_risk_management_and_compliance=user,
    )

    url = reverse("v1:cca-reject-cca", args=[cca.pk])
    data = {}

    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "data" in response.json()

    cca.refresh_from_db()
    assert cca.status == ComplianceCriticalityAssessment.Status.FOR_REVISION


@pytest.mark.django_db
def test_create_compliance_criticality_assessment(authenticated_user):
    api_client, user = authenticated_user

    url = reverse("v1:cca-list")
    data = {}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_compliance_criticality_assessment(authenticated_user):
    api_client, user = authenticated_user

    cca = ComplianceCriticalityAssessmentFactory(company=user.company)

    url = reverse("v1:cca-detail", args=[cca.pk])
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_compliance_criticality_assessment(authenticated_user):
    api_client, user = authenticated_user

    cca = ComplianceCriticalityAssessmentFactory(company=user.company)
    serialzier = ComplianceCriticalityAssessmentListSerializer(instance=cca)
    data = serialzier.data
    data["draft"] = True

    url = reverse("v1:cca-detail", args=[cca.pk])

    # update some editable fields
    data["solution_description"] = "some random text here"

    # update some readonly fields
    data["solution_classification"] = "this should not be saved"

    old_solution_classification = cca.solution_classification
    assert not cca.approved_by_business_owner
    assert not cca.approved_by_system_owner
    assert not cca.approved_by_it_risk_management_and_compliance

    response = api_client.put(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK

    cca.refresh_from_db()
    assert cca.solution_description == data["solution_description"]
    assert cca.solution_classification == old_solution_classification
    assert not cca.approved_by_business_owner
    assert not cca.approved_by_system_owner
    assert not cca.approved_by_it_risk_management_and_compliance


@pytest.mark.django_db
@patch("assessments.models.ComplianceCriticalityAssessment.run_generate_reports_chain")
def test_update_compliance_criticality_assessment_as_business_owner(
    mock_run_generate_reports_chain, authenticated_user
):
    api_client, user = authenticated_user

    cca = ComplianceCriticalityAssessmentFactory(
        company=user.company,
        business_owner=user,
        approved_by_business_owner=False,
        approved_by_system_owner=True,
        approved_by_it_risk_management_and_compliance=True,
    )
    serialzier = ComplianceCriticalityAssessmentListSerializer(instance=cca)
    data = serialzier.data
    data["draft"] = False

    url = reverse("v1:cca-detail", args=[cca.pk])

    assert not cca.approved_by_business_owner
    assert cca.approved_by_system_owner
    assert cca.approved_by_it_risk_management_and_compliance

    response = api_client.put(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK

    cca.refresh_from_db()
    # approval states should be reset
    assert cca.approved_by_business_owner
    assert cca.approved_by_system_owner
    assert cca.approved_by_it_risk_management_and_compliance
    assert cca.status == ComplianceCriticalityAssessment.Status.APPROVED


@pytest.mark.django_db
@patch("assessments.models.ComplianceCriticalityAssessment.run_generate_reports_chain")
def test_update_compliance_criticality_assessment_as_system_owner(
    mock_run_generate_reports_chain, authenticated_user
):
    api_client, user = authenticated_user

    cca = ComplianceCriticalityAssessmentFactory(
        company=user.company,
        system_owner=user,
        approved_by_business_owner=True,
        approved_by_system_owner=False,
        approved_by_it_risk_management_and_compliance=True,
        status=ComplianceCriticalityAssessment.Status.DRAFT,
    )
    serialzier = ComplianceCriticalityAssessmentListSerializer(instance=cca)
    data = serialzier.data
    data["draft"] = False

    url = reverse("v1:cca-detail", args=[cca.pk])

    assert cca.approved_by_business_owner
    assert not cca.approved_by_system_owner
    assert cca.approved_by_it_risk_management_and_compliance

    response = api_client.put(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK

    cca.refresh_from_db()
    assert cca.approved_by_business_owner
    assert cca.approved_by_system_owner
    assert cca.approved_by_it_risk_management_and_compliance
    assert cca.status == ComplianceCriticalityAssessment.Status.APPROVED


@pytest.mark.django_db
@patch("assessments.models.ComplianceCriticalityAssessment.run_generate_reports_chain")
def test_update_compliance_criticality_assessment_as_it_risk_management_and_compliance(
    mock_run_generate_reports_chain, authenticated_user
):
    api_client, user = authenticated_user

    cca = ComplianceCriticalityAssessmentFactory(
        company=user.company,
        it_risk_management_and_compliance=user,
        approved_by_business_owner=True,
        approved_by_system_owner=True,
        approved_by_it_risk_management_and_compliance=False,
    )
    serialzier = ComplianceCriticalityAssessmentListSerializer(instance=cca)
    data = serialzier.data
    data["draft"] = False

    url = reverse("v1:cca-detail", args=[cca.pk])

    assert cca.approved_by_business_owner
    assert cca.approved_by_system_owner
    assert not cca.approved_by_it_risk_management_and_compliance

    response = api_client.put(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK

    cca.refresh_from_db()
    assert cca.approved_by_business_owner
    assert cca.approved_by_system_owner
    assert cca.approved_by_it_risk_management_and_compliance
    assert cca.status == ComplianceCriticalityAssessment.Status.APPROVED


@pytest.mark.django_db
@patch("assessments.models.ComplianceCriticalityAssessment.run_generate_reports_chain")
def test_update_compliance_criticality_assessment_auto_approve_business_owner_when_user_is_an_approver(
    mock_run_generate_reports_chain, authenticated_user
):
    api_client, user = authenticated_user

    cca = ComplianceCriticalityAssessmentFactory(
        status=ComplianceCriticalityAssessment.Status.DRAFT,
        company=user.company,
        business_owner=user,
        approved_by_business_owner=None,
        approved_by_system_owner=None,
        approved_by_it_risk_management_and_compliance=None,
    )
    serialzier = ComplianceCriticalityAssessmentListSerializer(instance=cca)
    data = serialzier.data
    data["draft"] = False

    url = reverse("v1:cca-detail", args=[cca.pk])

    assert not cca.approved_by_business_owner
    assert not cca.approved_by_system_owner
    assert not cca.approved_by_it_risk_management_and_compliance

    response = api_client.put(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK

    cca.refresh_from_db()
    assert cca.approved_by_business_owner
    assert not cca.approved_by_system_owner
    assert not cca.approved_by_it_risk_management_and_compliance
    assert cca.status == ComplianceCriticalityAssessment.Status.FOR_REVIEW


@pytest.mark.django_db
@patch("assessments.models.ComplianceCriticalityAssessment.run_generate_reports_chain")
def test_update_compliance_criticality_assessment_auto_approve_system_owner_when_user_is_an_approver(
    mock_run_generate_reports_chain, authenticated_user
):
    api_client, user = authenticated_user

    cca = ComplianceCriticalityAssessmentFactory(
        status=ComplianceCriticalityAssessment.Status.DRAFT,
        company=user.company,
        system_owner=user,
        approved_by_business_owner=None,
        approved_by_system_owner=None,
        approved_by_it_risk_management_and_compliance=None,
    )
    serialzier = ComplianceCriticalityAssessmentListSerializer(instance=cca)
    data = serialzier.data
    data["draft"] = False

    url = reverse("v1:cca-detail", args=[cca.pk])

    assert not cca.approved_by_business_owner
    assert not cca.approved_by_system_owner
    assert not cca.approved_by_it_risk_management_and_compliance

    response = api_client.put(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK

    cca.refresh_from_db()
    assert not cca.approved_by_business_owner
    assert cca.approved_by_system_owner
    assert not cca.approved_by_it_risk_management_and_compliance
    assert cca.status == ComplianceCriticalityAssessment.Status.FOR_REVIEW


@pytest.mark.django_db
@patch("assessments.models.ComplianceCriticalityAssessment.run_generate_reports_chain")
def test_update_compliance_criticality_assessment_auto_approve_it_risk_management_and_compliance_when_user_is_an_approver(
    mock_run_generate_reports_chain, authenticated_user
):
    api_client, user = authenticated_user

    cca = ComplianceCriticalityAssessmentFactory(
        status=ComplianceCriticalityAssessment.Status.DRAFT,
        company=user.company,
        it_risk_management_and_compliance=user,
        approved_by_business_owner=None,
        approved_by_system_owner=None,
        approved_by_it_risk_management_and_compliance=None,
    )
    serialzier = ComplianceCriticalityAssessmentListSerializer(instance=cca)
    data = serialzier.data
    data["draft"] = False

    url = reverse("v1:cca-detail", args=[cca.pk])

    assert not cca.approved_by_business_owner
    assert not cca.approved_by_system_owner
    assert not cca.approved_by_it_risk_management_and_compliance

    response = api_client.put(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK

    cca.refresh_from_db()
    assert not cca.approved_by_business_owner
    assert not cca.approved_by_system_owner
    assert cca.approved_by_it_risk_management_and_compliance
    assert cca.status == ComplianceCriticalityAssessment.Status.FOR_REVIEW
