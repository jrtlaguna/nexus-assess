# Generated by Django 4.2.9 on 2024-01-23 08:56

from django.db import migrations, models


def update_solution_type(apps, schema_editor):
    ComplianceCriticalityAssessment = apps.get_model(
        "assessments", "ComplianceCriticalityAssessment"
    )

    # Update existing values to the corrected value
    # infrastructure was incorrectly spelled
    ComplianceCriticalityAssessment.objects.filter(
        solution_type="infrastucture"
    ).update(solution_type="infrastructure")


class Migration(migrations.Migration):
    dependencies = [
        (
            "assessments",
            "0011_alter_compliancecriticalityassessment_solution_type_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="compliancecriticalityassessment",
            name="solution_type",
            field=models.CharField(
                choices=[
                    ("application", "Application"),
                    ("infrastructure", "Infrastructure Platform"),
                    ("middleware", "Middleware"),
                    ("other", "Other"),
                ],
                max_length=50,
                null=True,
                verbose_name="Solution Type",
            ),
        ),
        migrations.RunPython(update_solution_type, migrations.RunPython.noop),
    ]
