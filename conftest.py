import pytest
from pytest_factoryboy import register

from django.conf import settings

from users.tests.factories import UserFactory

register(UserFactory)


@pytest.fixture(autouse=True)
def disable_s3_and_sendgrid():
    settings.STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
