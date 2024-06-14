from admin_auto_filters.filters import AutocompleteFilter

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.http.request import HttpRequest
from django.template.defaultfilters import pluralize
from django.utils.translation import gettext_lazy as _

from users.models import Company, User


class UserTypeFilter(admin.SimpleListFilter):
    title = "user type"
    parameter_name = "user_type"

    def lookups(self, request, model_admin):
        return User.UserType.choices

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(user_type=value)
        return queryset


class CompanyFilter(AutocompleteFilter):
    title = "Company"
    field_name = "company"


class UserInline(admin.StackedInline):
    model = User
    fields = [
        "email",
        "first_name",
        "last_name",
        "user_type",
    ]
    show_change_link = True
    extra = 1
    template = "admin/inline/user_stacked_inline.html"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request: HttpRequest, obj=None):
        return request.GET.get("_popup") is None


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_superuser=False)

    readonly_fields = ["is_active"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "user_type",
                    "is_superuser",
                    "company",
                )
            },
        ),
        ("", {"fields": ["is_active"]}),
    )
    list_display = [
        "email",
        "first_name",
        "last_name",
        "user_type",
        "company",
        "is_active",
        "is_superuser",
    ]
    search_fields = ["first_name", "last_name", "email", "company__name"]
    autocomplete_fields = ["company"]
    list_filter = [CompanyFilter, "is_active", UserTypeFilter, "is_superuser"]
    ordering = ["email"]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        if (
            "autocomplete" in request.path
            and request.GET.get("model_name") == "compliancecriticalityassessment"
        ):
            if request.GET.get("field_name") in [
                "business_owner",
                "system_owner",
                "it_risk_management_and_compliance",
            ]:
                queryset = queryset.filter(
                    is_active=True, user_type=User.UserType.CLIENT
                )
        return queryset, use_distinct

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            # If the user is not a superuser, remove 'is_superuser' from fieldsets
            fieldsets = [
                (
                    fieldset[0],
                    {
                        "fields": [
                            f for f in fieldset[1]["fields"] if f != "is_superuser"
                        ]
                    },
                )
                for fieldset in fieldsets
            ]
        return fieldsets

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        user = request.user
        return user.is_superuser

    @admin.action(description=_("Activate Users"))
    def activate_users(self, request, queryset):
        if not queryset:
            messages.error(request, _("Please select at least 1 user"))
        else:
            count = queryset.count()
            queryset.update(is_active=True)
            messages.success(
                request, _(f"Successfull activated {count} user{pluralize(count)}")
            )

    @admin.action(description=_("Deactivate Users"))
    def deactivate_users(self, request, queryset):
        if not queryset:
            messages.error(request, _("Please select at least 1 user"))
        else:
            count = queryset.count()
            queryset.update(is_active=False)
            messages.success(
                request, _(f"Successfull deactivated {count} user{pluralize(count)}")
            )

    actions = [
        deactivate_users,
        activate_users,
    ]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    readonly_fields = ["is_active"]
    search_fields = ["name"]
    list_filter = ["is_active"]
    inlines = [UserInline]
    list_display = [
        "name",
        "get_user_count",
        "is_active",
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def get_user_count(self, obj):
        return obj.users.count()

    get_user_count.short_description = "# of Users"
