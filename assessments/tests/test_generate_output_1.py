import os

import openpyxl
import pytest

from assessments.models import Report
from assessments.tests.factories import ComplianceCriticalityAssessmentFactory
from requirements.models import Requirement
from requirements.tests.factories import ComplianceFactory, RequirementFactory

from ..applogic.form_results_applogic import get_form_results
from ..applogic.generate_output_1 import generate_output_1, get_category

# First requirement control id in each category
requirement_control_id_list = [
    "CRS_AM-001",
    "CRS_CM-001",
    "CRS_DG-001",
    "CRS_DP-001",
    "CRS_DPri-001",
    "CRS_ERES-001",
    "CRS_IM-001",
    "CRS_IP-001",
    "CRS_LM-001",
    "CRS_PS-001",
    "CRS_RM-001",
    "CRS_SD-001",
    "CRS_SM-001",
    "CRS_TA-001",
]


@pytest.mark.django_db
def test_get_form_results_and_generate_export_1():
    ComplianceFactory(header_name="significant")
    ComplianceFactory(header_name="moderate")
    minimal_rating_compliance = ComplianceFactory(header_name="minimal")

    for req in requirement_control_id_list:
        RequirementFactory(
            control_id=req, baseline=True, compliances=[minimal_rating_compliance]
        )

    on_premises_cca = ComplianceCriticalityAssessmentFactory(
        hosting_and_type="on_premises"
    )
    # Simulating cca with minimal rating
    on_premises_cca.rating["rating_minimal"] = True
    on_premises_cca.rating["rating_no_compliance_risk"] = False

    cca_requirements = get_form_results(on_premises_cca)

    on_premises_hosting_requirements = Requirement.objects.filter(
        analytical_instruments=True
    )
    non_on_premises_hosting_requirements = Requirement.objects.filter(
        analytical_instruments=False
    )

    # Assert that every element in on_premises_hosting is in cca_requirements
    for requirement in on_premises_hosting_requirements:
        assert requirement in cca_requirements

    # Assert that each element in non_on_premises_hosting is not in cca_requirements
    for requirement in non_on_premises_hosting_requirements:
        assert requirement not in cca_requirements

    saas_cca = ComplianceCriticalityAssessmentFactory(hosting_and_type="saas")
    # Simulating cca with minimal rating
    saas_cca.rating["rating_minimal"] = True
    saas_cca.rating["rating_no_compliance_risk"] = False
    saas_cca_requirements = get_form_results(saas_cca)

    assert int(saas_cca_requirements.count()) != int(cca_requirements.count())

    # Assert that if rating is correct but baseline is false, it is not included in cca_requirements.
    modified_requirement = saas_cca_requirements.first()
    modified_requirement.baseline = False
    modified_requirement.save()

    saas_cca_requirements = get_form_results(saas_cca)

    assert modified_requirement not in saas_cca_requirements

    # Simulate requirement is not a baseline, but an impact classification
    modified_requirement.compliances.add(ComplianceFactory(header_name="sox"))
    saas_cca.sox_impact["is_solution_used_for_material_financial_data"] = True
    saas_cca.save()

    saas_cca_requirements = get_form_results(saas_cca)

    assert modified_requirement in saas_cca_requirements

    generate_output_1(saas_cca, saas_cca_requirements)

    export_1 = Report.objects.get(cca=saas_cca).output_xlsm_1

    assert export_1 is not None

    workbook = openpyxl.load_workbook(export_1.path)
    sheet = workbook.active

    # Shows the category at the top
    first_requirement = saas_cca_requirements.first()
    assert get_category(first_requirement.control_id) == sheet[1][0].value

    # Check that the category cell has the expected fill color and fill type
    expected_color = "00DDEBF7"
    expected_fill = "solid"
    first_cell = sheet.cell(row=1, column=1)
    assert first_cell.fill.start_color.rgb == expected_color
    assert first_cell.fill.end_color.rgb == expected_color
    assert first_cell.fill.fill_type == expected_fill

    # Displays the header under the first category
    assert "Requirement #" == sheet[2][0].value
    assert "Requirement Statement" == sheet[2][1].value
    assert "Comments" == sheet[2][2].value
    assert sheet[2][3].value is None  # Extra blank column
    assert "bbb Common Solution" == sheet[2][4].value
    assert "Test Guidance" == sheet[2][5].value

    # Shows the requirement information in the correct column
    assert first_requirement.control_id == sheet[3][0].value
    assert first_requirement.requirement_statement == sheet[3][1].value
    assert first_requirement.bbb_common_solution == sheet[3][4].value
    assert first_requirement.test_guidance == sheet[3][5].value

    os.unlink(export_1.path)


@pytest.mark.django_db
def test_get_category_from_control_id():
    categories = [
        "Access Management",
        "Capability Management",
        "Data Governance",
        "Data Protection",
        "Data Privacy",
        "Electronic Signatures, Digital Signatures and Electronic Records",
        "Incident Management",
        "Infrastructure Protection",
        "Logging & Monitoring",
        "Physical Security",
        "Risk Management",
        "Secure Development / SDLC",
        "Supplier Management",
        "Training & Awareness",
    ]

    for requirement in requirement_control_id_list:
        assert get_category(requirement) in categories

    with pytest.raises(AttributeError):
        get_category("Invalid Value")
