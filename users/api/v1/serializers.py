from dj_rest_auth import serializers as dj_rest_auth_serializers
from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from users.forms import AllAuthPasswordResetForm
from users.models import Company


class PasswordResetSerializer(dj_rest_auth_serializers.PasswordResetSerializer):
    password_reset_form_class = AllAuthPasswordResetForm


class PasswordChangeSerializer(dj_rest_auth_serializers.PasswordChangeSerializer):
    def custom_validation(self, attrs):
        if attrs.get("old_password") == attrs.get("new_password1"):
            err_msg = _("Your new password should not be the same as the old password.")
            raise serializers.ValidationError(err_msg)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "name")


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "first_name",
            "last_name",
            "user_type",
        )

    def validate_email(self, value):
        if value == "":
            raise serializers.ValidationError(_("Email field cannot be empty"))
        return value


class UserSerializer(BaseUserSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "first_name", "last_name", "company")

    def update(self, instance, validated_data):
        company_data = validated_data.pop("company", None)

        if company_data:
            company_serializer = self.fields["company"]
            company_instance = instance.company
            company_serializer.update(company_instance, company_data)

        return super().update(instance, validated_data)

    def validate(self, data):
        # Run the default validation first
        data = super().validate(data)

        try:
            first_name = data.get("first_name", self.instance.first_name)
            data["first_name"] = first_name.encode("ascii", "strict").decode("utf-8")
        except UnicodeEncodeError:
            raise serializers.ValidationError(
                {"first_name": ["Non-ascii characters not allowed in first name."]}
            )

        try:
            last_name = data.get("last_name", self.instance.last_name)
            data["last_name"] = last_name.encode("ascii", "strict").decode("utf-8")
        except UnicodeEncodeError:
            raise serializers.ValidationError(
                {"last_name": ["Non-ascii characters not allowed in last name."]}
            )

        return data
