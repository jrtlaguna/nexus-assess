# Generated by Django 4.2.10 on 2024-03-07 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "assessments",
            "0024_alter_compliancecriticalityassessment_approved_by_business_owner_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="compliancecriticalityassessment",
            name="solution_classification",
            field=models.CharField(
                choices=[
                    ("custom", "Custom"),
                    ("configurable", "Configurable"),
                    ("non_configurable", "Non-configurable (out-of-the-box)"),
                ],
                max_length=50,
                null=True,
                verbose_name="Solution Classification",
            ),
        ),
    ]
