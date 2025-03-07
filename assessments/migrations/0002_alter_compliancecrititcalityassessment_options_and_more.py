# Generated by Django 4.2.7 on 2023-12-06 12:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("assessments", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="compliancecrititcalityassessment",
            options={
                "verbose_name": "Compliance Crititcality Assessment",
                "verbose_name_plural": "Compliance Crititcality Assessments",
            },
        ),
        migrations.AddField(
            model_name="report",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Created At"
            ),
        ),
        migrations.AddField(
            model_name="report",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Updated At"),
        ),
    ]
