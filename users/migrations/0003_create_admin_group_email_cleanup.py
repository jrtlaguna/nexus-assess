from django.db import migrations
from django.db.models import Count

from users.models import User


class Migration(migrations.Migration):
    def update_duplicate_emails(apps, schema_editor):
        email_list = (
            User.objects.values("email")
            .annotate(similar_id=Count("id"))
            .filter(similar_id__gte=2)
            .values_list("email", flat=True)
        )
        for email in email_list:
            at_index = email.find("@")
            for index, user in enumerate(User.objects.filter(email=email)):
                if index == 0:
                    continue
                user.email = email[:at_index] + str(index) + email[at_index:]
                user.save()

    dependencies = [
        ("users", "0002_company_user_user_type_alter_user_is_active_and_more"),
    ]

    operations = [
        migrations.RunPython(update_duplicate_emails, migrations.RunPython.noop),
    ]
