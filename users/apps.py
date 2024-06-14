from django.apps import AppConfig, apps
from django.db.models import Q
from django.db.models.signals import post_migrate


def create_group_and_assign_permissions(sender, **kwargs):
    user_model = apps.get_model("users", "User")
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")

    permissions = permission_model.objects.filter(
        Q(codename__icontains="user") | Q(codename__icontains="company"),
        ~Q(codename__icontains="delete"),
    )
    group, _ = group_model.objects.get_or_create(name="Admins")
    group.permissions.add(*permissions.values_list("id", flat=True))

    if users := user_model.objects.filter(user_type=user_model.UserType.ADMINISTRATOR):
        group.user_set.add(*users.values_list("id", flat=True))


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        post_migrate.connect(create_group_and_assign_permissions, sender=self)
