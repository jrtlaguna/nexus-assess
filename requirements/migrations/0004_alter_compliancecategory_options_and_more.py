# Generated by Django 4.2.9 on 2024-02-08 03:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("requirements", "0003_alter_compliance_header_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="compliancecategory",
            options={
                "verbose_name": "Compliance Category",
                "verbose_name_plural": "Compliance Categories",
            },
        ),
        migrations.AlterModelOptions(
            name="referencecategory",
            options={
                "verbose_name": "Reference Category",
                "verbose_name_plural": "Reference Categories",
            },
        ),
        migrations.AlterModelOptions(
            name="referencepolicy",
            options={
                "verbose_name": "Reference Policy",
                "verbose_name_plural": "Reference Policies",
            },
        ),
        migrations.AlterModelOptions(
            name="requirementcategory",
            options={
                "verbose_name": "Requirement Category",
                "verbose_name_plural": "Requirement Categories",
            },
        ),
    ]
