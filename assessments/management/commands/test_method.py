from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        from assessments.applogic import generate_docx_output
        from assessments.models import ComplianceCriticalityAssessment

        cca = ComplianceCriticalityAssessment.objects.last()
        generate_docx_output(cca)
