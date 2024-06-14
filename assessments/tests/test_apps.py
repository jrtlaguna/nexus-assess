import pytest

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from ..apps import assign_permissions
from ..models import ComplianceCriticalityAssessment, Report, ReviewComment


@pytest.mark.django_db
def test_assign_permissions():
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")

    # Create a temporary permission for testing
    test_assessment_permission = permission_model.objects.create(
        codename="test_assessment_permission",
        name="Test Assessment Permission",
        content_type=ContentType.objects.get_for_model(ComplianceCriticalityAssessment),
    )

    test_report_permission = permission_model.objects.create(
        codename="test_report_permission",
        name="Test Report Permission",
        content_type=ContentType.objects.get_for_model(Report),
    )

    test_comment_permission = permission_model.objects.create(
        codename="test_reviewcomment_permission",
        name="Test Comment Permission",
        content_type=ContentType.objects.get_for_model(ReviewComment),
    )

    test_other_permission = permission_model.objects.create(
        codename="test_other_permission",
        name="Test Other Permission",
        content_type=ContentType.objects.get_for_model(ReviewComment),
    )

    assign_permissions(None)  # sender value does not matter here
    admins_group, created = group_model.objects.get_or_create(name="Admins")

    assert test_assessment_permission in admins_group.permissions.all()
    assert test_report_permission in admins_group.permissions.all()
    assert test_comment_permission in admins_group.permissions.all()
    assert test_other_permission not in admins_group.permissions.all()

    test_assessment_permission.delete()
    test_report_permission.delete()
    test_comment_permission.delete()
    test_other_permission.delete()
