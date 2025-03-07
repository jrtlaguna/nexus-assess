# Generated by Django 4.2.7 on 2023-12-06 11:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ComplianceCrititcalityAssessment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "solution_name",
                    models.CharField(max_length=256, verbose_name="Solution Name"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "output_xlsm_1",
                    models.FileField(upload_to="", verbose_name="Output XLSM 1"),
                ),
                (
                    "output_xlsm_2",
                    models.FileField(upload_to="", verbose_name="Output XLSM 2"),
                ),
                (
                    "output_csv_1",
                    models.FileField(upload_to="", verbose_name="Output CSV 1"),
                ),
                (
                    "output_docx_1",
                    models.FileField(upload_to="", verbose_name="Output Docx 1"),
                ),
                (
                    "cca",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="assessments.compliancecrititcalityassessment",
                        verbose_name="Criticality Assessment",
                    ),
                ),
            ],
            options={
                "verbose_name": "Report",
                "verbose_name_plural": "Reports",
            },
        ),
    ]
