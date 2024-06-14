from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import OPTIONAL


class Requirement(models.Model):
    control_id = models.CharField(verbose_name=_("Control ID"), max_length=50)
    control_statement = models.TextField(verbose_name=_("Control Statement"))
    requirement_statement = models.TextField(verbose_name=_("Requirement Statement"))
    test_guidance = models.TextField(verbose_name=_("Test Guidance"), **OPTIONAL)
    organization = models.BooleanField(verbose_name=_("Organization"), default=False)
    analytical_instruments = models.BooleanField(
        _("Analytical Instruments"), default=False
    )
    saas_application = models.BooleanField(_("SaaS/Application"), default=False)
    paas = models.BooleanField(_("PaaS"), default=False)
    iaas_infrastructure = models.BooleanField(_("IaaS/Infrastructure"), default=False)
    category = models.ForeignKey(
        "requirements.RequirementCategory",
        verbose_name=_("Category"),
        on_delete=models.CASCADE,
    )
    compliances = models.ManyToManyField(
        "requirements.Compliance", verbose_name=_("Compliances")
    )
    references = models.ManyToManyField(
        "requirements.Reference",
        verbose_name=_("References"),
    )
    baseline = models.BooleanField(_("Baseline"), default=False)
    bbb_common_solution = models.TextField(_("bbb Common Solution"), **OPTIONAL)

    def __str__(self):
        return self.control_id

    def save(self, *args, **kwargs):
        # TODO: check if organization, else should have solution_types
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Requirement")
        verbose_name_plural = _("Requirements")


class RequirementCategory(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Requirement Category")
        verbose_name_plural = _("Requirement Categories")


class Compliance(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=256)
    category = models.ForeignKey(
        "requirements.ComplianceCategory", on_delete=models.CASCADE
    )
    header_name = models.CharField(
        verbose_name=_("Header Name"), max_length=50, **OPTIONAL
    )
    reference_policies = models.ManyToManyField(
        "requirements.ReferencePolicy",
        verbose_name=_("Related Reference Policies"),
        blank=True,
    )

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    class Meta:
        verbose_name = _("Compliance")
        verbose_name_plural = _("Compliance")


class ComplianceCategory(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Compliance Category")
        verbose_name_plural = _("Compliance Categories")


class Reference(models.Model):
    identifier = models.CharField(verbose_name=_("Identifier"), max_length=256)
    policy = models.ForeignKey(
        "requirements.ReferencePolicy",
        verbose_name=_("Reference Policy"),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.policy} - {self.identifier}"

    class Meta:
        verbose_name = _("Reference")
        verbose_name_plural = _("References")


class ReferencePolicy(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=256)
    category = models.ForeignKey(
        "requirements.ReferenceCategory",
        verbose_name=_("Category"),
        on_delete=models.CASCADE,
    )
    header_name = models.CharField(_("Header Name"), max_length=50, **OPTIONAL)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    class Meta:
        verbose_name = _("Reference Policy")
        verbose_name_plural = _("Reference Policies")


class ReferenceCategory(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Reference Category")
        verbose_name_plural = _("Reference Categories")
