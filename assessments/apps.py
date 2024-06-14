from django.apps import AppConfig, apps
from django.db.models import Q
from django.db.models.signals import post_migrate


def assign_permissions(sender, **kwargs):
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")

    permissions = permission_model.objects.filter(
        (
            Q(codename__icontains="assessment")
            | Q(codename__icontains="report")
            | Q(codename__icontains="review")
            | Q(codename__icontains="export")
        ),
        ~Q(codename__icontains="delete"),
    )
    group, _ = group_model.objects.get_or_create(name="Admins")
    group.permissions.add(*permissions.values_list("id", flat=True))


class AssessmentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "assessments"

    def ready(self):
        post_migrate.connect(assign_permissions, sender=self)
