from unittest import mock

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from core.api.v1.views import ContactUsView
from users.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
def test_contact_us_view_success():
    factory = APIRequestFactory()
    url = reverse("v1:contact_us")

    data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "subject": "Test Subject",
        "message": "Test Message",
    }

    # Creating an administrator user for testing purposes
    admin_user = UserFactory(
        user_type=User.UserType.ADMINISTRATOR,
        is_active=True,
        is_superuser=True,
        is_staff=True,
    )

    # Creating a non-admin user for testing purposes
    non_admin_user = UserFactory(user_type=User.UserType.CLIENT, is_active=True)

    user = UserFactory()
    request = factory.post(url, data, format="json")
    force_authenticate(request, user)

    view = ContactUsView.as_view()
    with mock.patch(
        "core.api.v1.views.send_contact_us_emails_to_admin.delay"
    ) as mock_send_email_delay:
        mock_send_email_delay.reset_mock()
        response = view(request)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {"success": "Message sent successfully"}

        # Assert that send_contact_us_emails_to_admin.delay was called with the expected arguments
        mock_send_email_delay.assert_called_once_with(
            [admin_user.id],
            {
                "logo": mock.ANY,
                "top_line_art_url": mock.ANY,
                "bottom_line_art_url": mock.ANY,
                "date_submitted": mock.ANY,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "subject": "Test Subject",
                "message": "Test Message",
            },
        )


@pytest.mark.django_db
def test_contact_us_view_missing_fields():
    factory = APIRequestFactory()
    url = reverse("v1:contact_us")

    data = {
        "name": "John Doe",
        "subject": "Test Subject",
        # Missing 'email' and 'message' fields intentionally
    }

    user = UserFactory()
    request = factory.post(url, data, format="json")
    force_authenticate(request, user)

    view = ContactUsView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "Name, Email, and Message fields are required."}


@pytest.mark.django_db
def test_contact_us_view_unauthenticated():
    factory = APIRequestFactory()
    url = reverse("v1:contact_us")

    data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "subject": "Test Subject",
        "message": "Test Message",
    }

    request = factory.post(url, data, format="json")
    view = ContactUsView.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"detail": "Authentication credentials were not provided."}
