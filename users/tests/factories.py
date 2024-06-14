import factory
from factory import Faker, post_generation

from django.contrib.auth import get_user_model

from ..models import Company

User = get_user_model()


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    user_type = User.UserType.CLIENT
    is_active = True
    is_superuser = False
    is_staff = False

    @post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password("password")

    class Meta:
        model = User
        django_get_or_create = ["email"]
