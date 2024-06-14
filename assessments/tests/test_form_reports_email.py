import tempfile
from unittest.mock import patch

import pytest

from django.core import mail

from assessments.models import Report
from assessments.tasks import send_form_reports_email
from assessments.tests.factories import ComplianceCriticalityAssessmentFactory


@pytest.mark.django_db
@patch("assessments.models.ComplianceCriticalityAssessment.run_generate_reports_chain")
def test_ready_forms_report_email(*args):
    (mock_run_generate_reports_chain,) = args
    cca = ComplianceCriticalityAssessmentFactory(
        solution_name="Solution 1",
        approved_by_business_owner=True,
        approved_by_system_owner=True,
        approved_by_it_risk_management_and_compliance=True,
    )
    report = Report.objects.get(cca=cca)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Your data here")
        report.compressed_reports = temp_file.name
        report.save()
        assert cca.status.value == "approved"
        mock_run_generate_reports_chain.assert_called_once()
        send_form_reports_email("", cca.id)

        assert len(mail.outbox) == 1
        assert (
            mail.outbox[0].subject
            == "Nexus - Form Report Ready For Download Notification"
        )
        assert cca.drafted_by.email in mail.outbox[0].to
