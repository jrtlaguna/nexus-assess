import pytest

from django.contrib import admin

from users.tests.factories import CompanyFactory, UserFactory

from .. import applogic as assessment_applogic
from ..admin import (
    ComplianceCritcalityAssessmentAdmin,
    ComplianceCriticalityAssessmentAdminForm,
)
from ..models import ComplianceCriticalityAssessment


@pytest.fixture
def admin_instance():
    return ComplianceCritcalityAssessmentAdmin(
        ComplianceCriticalityAssessment, admin.site
    )


@pytest.fixture
def invalid_form_data():
    return {"somekey": "somevalue"}


@pytest.fixture
def required_form_data():
    company = CompanyFactory()
    return {
        "company": company,
        "drafted_by": UserFactory(company=company),
        "business_owner": UserFactory(company=company),
        "system_owner": UserFactory(company=company),
        "it_risk_management_and_compliance": UserFactory(company=company),
        "status": ComplianceCriticalityAssessment.Status.DRAFT,
        "solution_name": "Solution A",
        "vendor_name": "Vendor 1",
        "solution_type": ComplianceCriticalityAssessment.SolutionType.APPLICATION,
        "hosting_and_type": ComplianceCriticalityAssessment.HostingAndType.IAAS,
        "server_host": "USA",
        "solution_classification": ComplianceCriticalityAssessment.SolutionClassification.CONFIGURABLE,
        "gxp_impact": {},
        "gxp_eres": {},
        "sox_impact": {},
        "privacy_impact": {},
        "data_classification": {},
        "business_impact": {},
        "summary": {},
        "rating": {},
    }


@pytest.mark.django_db
def test_validate_gxp_impact_valid(required_form_data):
    valid_gxp_impact_data = assessment_applogic.get_default_gxp_impact_json_value()
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=valid_gxp_impact_data)

    # Validating the gxp_impact data
    cleaned_data = form.validate_gxp_impact(valid_gxp_impact_data)

    # Check if the cleaned data is correctly assigned
    assert "gxp_impact" in cleaned_data
    assert cleaned_data["gxp_impact"] == valid_gxp_impact_data["gxp_impact"]


@pytest.mark.django_db
def test_validate_gxp_impact_invalid(invalid_form_data, required_form_data):
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=required_form_data)
    form.validate_gxp_impact(invalid_form_data)
    error = form.non_field_errors()[0]

    assert error.startswith("Data is missing the following fields")


@pytest.mark.django_db
def test_validate_gxp_eres_valid(required_form_data):
    valid_gxp_eres_data = assessment_applogic.get_default_gxp_eres_json_value()
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=valid_gxp_eres_data)

    # Validating the gxp_eres data
    cleaned_data = form.validate_gxp_eres(valid_gxp_eres_data)

    # Check if the cleaned data is correctly assigned
    assert "gxp_eres" in cleaned_data
    assert cleaned_data["gxp_eres"] == valid_gxp_eres_data["gxp_eres"]


@pytest.mark.django_db
def test_validate_gxp_eres_invalid(invalid_form_data, required_form_data):
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=required_form_data)
    form.validate_gxp_eres(invalid_form_data)

    error = form.non_field_errors()[0]
    assert error.startswith("Data is missing the following fields")


@pytest.mark.django_db
def test_validate_sox_impact_valid(required_form_data):
    valid_sox_impact_data = assessment_applogic.get_default_sox_impact_json_value()
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=valid_sox_impact_data)

    # Validating the sox_impact data
    cleaned_data = form.validate_sox_impact(valid_sox_impact_data)

    # Check if the cleaned data is correctly assigned
    assert "sox_impact" in cleaned_data
    assert cleaned_data["sox_impact"] == valid_sox_impact_data["sox_impact"]


@pytest.mark.django_db
def test_validate_sox_impact_invalid(invalid_form_data, required_form_data):
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=required_form_data)
    form.validate_sox_impact(invalid_form_data)

    error = form.non_field_errors()[0]
    assert error.startswith("Data is missing the following fields")


@pytest.mark.django_db
def test_validate_privacy_impact_valid(required_form_data):
    valid_privacy_impact_data = (
        assessment_applogic.get_default_privacy_impact_json_value()
    )
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=valid_privacy_impact_data)

    # Validating the privacy_impact data
    cleaned_data = form.validate_privacy_impact(valid_privacy_impact_data)

    # Check if the cleaned data is correctly assigned
    assert "privacy_impact" in cleaned_data
    assert cleaned_data["privacy_impact"] == valid_privacy_impact_data["privacy_impact"]


@pytest.mark.django_db
def test_validate_privacy_impact_invalid(invalid_form_data, required_form_data):
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=required_form_data)
    form.validate_privacy_impact(invalid_form_data)

    error = form.non_field_errors()[0]
    assert error.startswith("Data is missing the following fields")


@pytest.mark.django_db
def test_validate_data_classification_valid(required_form_data):
    valid_data_classification_data = (
        assessment_applogic.get_default_data_classification_json_value()
    )
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=valid_data_classification_data)

    # Validating the data_classification data
    cleaned_data = form.validate_data_classification(valid_data_classification_data)

    # Check if the cleaned data is correctly assigned
    assert "data_classification" in cleaned_data
    assert (
        cleaned_data["data_classification"]
        == valid_data_classification_data["data_classification"]
    )


@pytest.mark.django_db
def test_validate_data_classification_invalid(invalid_form_data, required_form_data):
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=required_form_data)
    form.validate_data_classification(invalid_form_data)

    error = form.non_field_errors()[0]
    assert error.startswith("Data is missing the following fields")


@pytest.mark.django_db
def test_validate_business_impact_valid(required_form_data):
    valid_business_impact_data = (
        assessment_applogic.get_default_business_impact_json_value()
    )
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=valid_business_impact_data)

    # Validating the business_impact data
    cleaned_data = form.validate_business_impact(valid_business_impact_data)

    # Check if the cleaned data is correctly assigned
    assert "business_impact" in cleaned_data
    assert (
        cleaned_data["business_impact"] == valid_business_impact_data["business_impact"]
    )


@pytest.mark.django_db
def test_validate_business_impact_invalid(invalid_form_data, required_form_data):
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=required_form_data)
    form.validate_business_impact(invalid_form_data)

    error = form.non_field_errors()[0]
    assert error.startswith("Data is missing the following fields")


@pytest.mark.django_db
def test_validate_approvers_valid(required_form_data):
    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=required_form_data)
    form.validate_approvers(required_form_data)

    assert not "business_owner" in form.errors
    assert not "system_owner" in form.errors
    assert not "it_risk_management_and_compliance" in form.errors


@pytest.mark.django_db
def test_validate_approvers_invalid(required_form_data):
    company2 = CompanyFactory(name="Company 2")
    invalid_approvers = required_form_data
    invalid_approvers.update(
        {
            "business_owner": UserFactory(company=company2),
            "system_owner": UserFactory(company=company2),
            "it_risk_management_and_compliance": UserFactory(company=company2),
        }
    )

    # Instantiate the form with the required data just so we can get past the initial clean
    form = ComplianceCriticalityAssessmentAdminForm(data=required_form_data)
    form.validate_approvers(invalid_approvers)

    assert "business_owner" in form.errors
    assert "system_owner" in form.errors
    assert "it_risk_management_and_compliance" in form.errors


def test_cca_admin_get_fieldsets_add_fieldsets(admin_instance):
    fieldsets = admin_instance.get_fieldsets(request=None, obj=None)

    # Ensure that add_fieldsets are returned for obj=None
    assert fieldsets == admin_instance.add_fieldsets


def test_cca_admin_get_fieldsets_existing_obj(admin_instance):
    obj = ComplianceCriticalityAssessment()
    fieldsets = admin_instance.get_fieldsets(request=None, obj=obj)

    # Ensure that fieldsets include the additional fieldsets based on conditions
    assert any("GXP Impact" in fs[0] for fs in fieldsets if fs[0])
    assert any(
        "GxP Electronic Records (ER) and Electronic Signatures (ES) Applicability"
        in fs[0]
        for fs in fieldsets
        if fs[0]
    )
    assert any("SOX Impact" in fs[0] for fs in fieldsets if fs[0])
    assert any("Privacy Impact" in fs[0] for fs in fieldsets if fs[0])
    assert any("Data Classification" in fs[0] for fs in fieldsets if fs[0])
    assert any("Business Impact" in fs[0] for fs in fieldsets if fs[0])
    assert any("Solution Criticality Summary" in fs[0] for fs in fieldsets if fs[0])
    assert any("Compliance Criticality Rating" in fs[0] for fs in fieldsets if fs[0])
