from admin_auto_filters.filters import AutocompleteFilter

from django.contrib import admin

from requirements.models import (
    Compliance,
    ComplianceCategory,
    Reference,
    ReferenceCategory,
    ReferencePolicy,
    Requirement,
    RequirementCategory,
)


class CategoryFilter(AutocompleteFilter):
    title = "Category"
    field_name = "category"


class ReferenceInline(admin.TabularInline):
    model = Reference


class ReferencePolicyFilter(AutocompleteFilter):
    title = "Referemce Policy"
    field_name = "policy"


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    fieldsets = fieldsets = (
        (None, {"fields": ["control_id"]}),
        (
            "Main Fields",
            {
                "fields": (
                    "category",
                    "control_statement",
                    "requirement_statement",
                    "test_guidance",
                    "bbb_common_solution",
                )
            },
        ),
        (
            "Organization and Solution Type",
            {
                "fields": [
                    "organization",
                    "analytical_instruments",
                    "saas_application",
                    "paas",
                    "iaas_infrastructure",
                ]
            },
        ),
        ("Compliances", {"fields": ["compliances"]}),
        ("References", {"fields": ["baseline", "references"]}),
    )
    list_display = [
        "control_id",
        "category",
        "control_statement",
        "requirement_statement",
        "baseline",
    ]
    autocomplete_fields = ["category"]
    search_fields = ["control_id", "category__name"]
    list_filter = [
        CategoryFilter,
        "organization",
        "analytical_instruments",
        "saas_application",
        "paas",
        "iaas_infrastructure",
        "baseline",
    ]
    filter_horizontal = ["compliances", "references"]
    ordering = ["control_id"]


@admin.register(RequirementCategory)
class RequirementCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(ComplianceCategory)
class ComplianceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Compliance)
class ComplianceAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
    ]
    search_fields = ["name", "category__name"]
    list_filter = ["category"]
    autocomplete_fields = ["category"]
    ordering = ["category__name", "name"]
    filter_horizontal = ["reference_policies"]
    readonly_fields = ["header_name"]


@admin.register(ReferenceCategory)
class ReferenceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(ReferencePolicy)
class ReferencePolicyAdmin(admin.ModelAdmin):
    list_display = ["name", "category"]
    search_fields = ["name", "category__name"]
    list_filter = ["category"]
    autocomplete_fields = ["category"]
    ordering = ["category__name", "name"]
    readonly_fields = ["header_name"]


@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ["identifier", "policy"]
    search_fields = ["identifier", "policy__name"]
    ordering = ["policy__category__name", "policy__name", "identifier"]
    list_filter = [ReferencePolicyFilter]
