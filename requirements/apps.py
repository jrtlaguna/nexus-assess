from django.apps import AppConfig, apps
from django.db.models import Q
from django.db.models.signals import post_migrate


def assign_permissions(sender, **kwargs):
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")

    permissions = permission_model.objects.filter(
        Q(codename__icontains="requirement")
        | Q(codename__icontains="compliance")
        | Q(codename__icontains="reference"),
        ~Q(codename__icontains="delete"),
    )

    group, _ = group_model.objects.get_or_create(name="Admins")
    group.permissions.add(*permissions.values_list("id", flat=True))


class RequirementsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "requirements"

    def ready(self):
        post_migrate.connect(assign_permissions, sender=self)
