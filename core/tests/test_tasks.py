import pytest

from django.contrib.auth import get_user_model
from django.core import mail

from users.tests.factories import UserFactory

from ..tasks import send_contact_us_emails_to_admin

User = get_user_model()


@pytest.mark.django_db
def test_send_contact_us_emails_to_admin():
    user1 = UserFactory(
        user_type=User.UserType.ADMINISTRATOR,
        is_active=True,
        is_superuser=True,
        is_staff=True,
    )
    user2 = UserFactory(
        user_type=User.UserType.ADMINISTRATOR,
        is_active=True,
        is_superuser=True,
        is_staff=True,
    )
    user3 = UserFactory(
        user_type=User.UserType.CLIENT,
        is_active=True,
        is_superuser=False,
        is_staff=False,
    )

    send_contact_us_emails_to_admin([user1.id, user2.id, user3.id], {})

    assert len(mail.outbox) == 1
    expected_recipients = [user1.email, user2.email]
    for email in mail.outbox:
        assert email.subject == "Nexus - Contact Us Submission Notification"
        assert set(email.recipients()) == set(expected_recipients)
