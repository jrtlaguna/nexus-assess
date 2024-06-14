from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

from users.models import User


class UserDeactivateView(View):
    def get(self, request, *args, **kwargs):
        # Your custom action logic here
        user: User = request.user
        if user.is_superadmin or user.user_type == user.UserType.ADMINISTRATOR:
            messages.success(request, "Custom action performed successfully.")
        return redirect(
            reverse("admin:yourapp_yourmodel_change", args=[kwargs["object_id"]])
        )
