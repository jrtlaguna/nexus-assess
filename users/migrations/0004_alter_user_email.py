# Generated by Django 4.2.8 on 2024-01-02 06:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_create_admin_group_email_cleanup"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
