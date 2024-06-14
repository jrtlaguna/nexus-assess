from io import BytesIO
from unittest.mock import Mock, patch

import pytest

from django.core import mail

from users.tests.factories import UserFactory

from ..applogic.form_results_applogic import get_form_results
from ..models import AssessmentExport, ComplianceCriticalityAssessment
from ..tasks import (
    compress_reports_and_save_to_model,
    create_and_email_export,
    create_assessment_export,
    create_output_1,
    create_output_2,
)
from .factories import ComplianceCriticalityAssessmentFactory


@pytest.mark.django_db
def test_compress_reports_and_save_to_model():
    cca = ComplianceCriticalityAssessmentFactory()

    # Mock storage.open and zipfile.ZipFile
    with patch("django.core.files.storage.default_storage.open") as mock_open, patch(
        "zipfile.ZipFile"
    ) as mock_zipfile:

        # Set up mock behavior
        mock_open.side_effect = lambda x: BytesIO(b"Mocked File Content")
        mock_zipfile_instance = mock_zipfile.return_value
        mock_zipfile_instance.__enter__.return_value = mock_zipfile_instance

        # Call the task
        result = compress_reports_and_save_to_model(None, cca.id)

        # Assert that the task completed successfully
        assert result == {
            "message": "Reports have been compiled and zipped",
            "success": True,
        }
        cca.refresh_from_db()
        assert cca.report.compressed_reports is not None


@pytest.mark.django_db
def test_create_output_1():
    # Create a ComplianceCriticalityAssessment
    cca = ComplianceCriticalityAssessmentFactory(
        hosting_and_type=ComplianceCriticalityAssessment.HostingAndType.IAAS
    )
    requirements = get_form_results(cca)

    # Mock generate_output_1
    with patch(
        "assessments.applogic.generate_output_1.generate_output_1"
    ) as mock_generate_output_1:
        # Set up mock behavior
        mock_generate_output_1.return_value = None

        # Call the task
        result = create_output_1(
            {
                "requirement_ids": list(requirements.values_list("id", flat=True)),
                "success": True,
            },
            cca.id,
        )

        # Assert that the task completed successfully
        assert result == {
            "message": "Output 1 generated successfully.",
            "requirement_ids": [],
            "success": True,
        }

        # Assert that generate_output_1 was called with the correct argument
        mock_generate_output_1.assert_called_once()


@pytest.mark.django_db
def test_create_output_2():
    # Create a ComplianceCriticalityAssessment
    cca = ComplianceCriticalityAssessmentFactory(
        hosting_and_type=ComplianceCriticalityAssessment.HostingAndType.IAAS
    )
    requirements = get_form_results(cca)

    # Mock generate_output_2
    with patch(
        "assessments.applogic.generate_output_2.generate_output_2"
    ) as mock_generate_output_2:
        # Set up mock behavior
        mock_generate_output_2.return_value = None

        # Call the task
        result = create_output_2(
            {
                "requirement_ids": list(requirements.values_list("id", flat=True)),
                "success": True,
            },
            cca.id,
        )

        # Assert that the task completed successfully
        assert result == {
            "message": "Output 2 generated successfully.",
            "success": True,
        }

        # Assert that generate_output_2 was called with the correct argument
        mock_generate_output_2.assert_called_once()


@pytest.mark.django_db
def test_create_assessment_export():
    user = UserFactory()

    with patch(
        "assessments.applogic.csv_export_applogic.convert_to_dataframe"
    ) as mock_convert_to_dataframe:
        result = create_assessment_export([], user.id)

        assert isinstance(result, AssessmentExport)
        assert result.exported_by == user
        assert result.document_file is not None


class MockAssessmentExport:
    def __init__(self):
        self.document_file = Mock()


@pytest.mark.django_db
def test_create_and_email_export():
    user = UserFactory()
    mail.outbox = []

    with patch(
        "assessments.tasks.create_assessment_export"
    ) as mock_create_assessment_export:
        mock_create_assessment_export.return_value = MockAssessmentExport()

        create_and_email_export([], user.id)

        mock_create_assessment_export.assert_called_with([], user.id)
        assert len(mail.outbox) == 1
        assert (
            mail.outbox[0].subject
            == "Nexus - CCA Export Ready For Download Notification"
        )
        assert mail.outbox[0].recipients() == [user.email]
