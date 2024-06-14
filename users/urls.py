from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .api.v1 import views

urlpatterns = [
    path("", views.UserDetailsView.as_view(), name="user_details"),
    path("deactivate/", views.DeactivateUserView.as_view(), name="deactivate_user"),
]
