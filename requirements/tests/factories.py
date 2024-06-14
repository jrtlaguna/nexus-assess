import factory
from factory import Faker, SubFactory, post_generation

from django.utils.text import slugify

from ..models import (
    Compliance,
    ComplianceCategory,
    Reference,
    ReferenceCategory,
    ReferencePolicy,
    Requirement,
    RequirementCategory,
)


class RequirementCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RequirementCategory

    name = Faker("word")


class ComplianceCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceCategory

    name = Faker("word")


class ReferenceCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReferenceCategory

    name = Faker("word")


class ReferencePolicyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ReferencePolicy

    name = Faker("word")
    category = SubFactory(ReferenceCategoryFactory)
    header_name = Faker("word")


class ComplianceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Compliance

    name = Faker("word")
    category = SubFactory(ComplianceCategoryFactory)
    header_name = Faker("word")

    @post_generation
    def reference_policies(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for policy in extracted:
                self.reference_policies.add(policy)
        else:
            self.reference_policies.add(ReferencePolicyFactory())


class ReferenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reference

    identifier = Faker("word")
    policy = SubFactory(ReferencePolicyFactory)


class RequirementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Requirement

    control_id = Faker("word")
    control_statement = Faker("text")
    requirement_statement = Faker("text")
    test_guidance = Faker("text")
    organization = Faker("boolean")
    analytical_instruments = Faker("boolean")
    saas_application = Faker("boolean")
    paas = Faker("boolean")
    iaas_infrastructure = Faker("boolean")
    category = SubFactory(RequirementCategoryFactory)
    baseline = Faker("boolean")
    bbb_common_solution = Faker("text")

    @post_generation
    def compliances(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for compliance in extracted:
                self.compliances.add(compliance)
        else:
            self.compliances.add(ComplianceFactory())

    @post_generation
    def references(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for reference in extracted:
                self.references.add(reference)
        else:
            self.references.add(ReferenceFactory())
