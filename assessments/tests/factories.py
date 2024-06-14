import factory
from factory import Faker

from users.tests.factories import CompanyFactory, UserFactory

from ..models import ComplianceCriticalityAssessment, Report, ReviewComment


class ComplianceCriticalityAssessmentFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    company = factory.SubFactory(CompanyFactory, name=factory.Faker("company"))
    drafted_by = factory.SubFactory(UserFactory)
    business_owner = factory.SubFactory(UserFactory)
    system_owner = factory.SubFactory(UserFactory)
    it_risk_management_and_compliance = factory.SubFactory(UserFactory)

    class Meta:
        model = ComplianceCriticalityAssessment


class ReviewCommentFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    cca = factory.SubFactory(ComplianceCriticalityAssessmentFactory)

    class Meta:
        model = ReviewComment
