import os

import pandas as pd
import pytest

from django.apps import apps
from django.conf import settings
from django.core.management import call_command

from requirements.applogic.import_source_table import import_source_table


@pytest.mark.django_db
def test_source_table_import():
    requirement_model = apps.get_model("requirements", "Requirement")
    requirement_category_model = apps.get_model("requirements", "RequirementCategory")
    reference_model = apps.get_model("requirements", "Reference")

    df = pd.read_excel(
        os.path.join(settings.STATICFILES_DIRS[0], "data/test_crs.xlsx"),
        sheet_name="Sheet1",
    )
    new_df_columns = import_source_table(df).columns.tolist()
    requirement = requirement_model.objects.first()
    non_organization_fields = [
        "analytical_instruments",
        "saas_application",
        "paas",
        "iaas_infrastructure",
    ]
    assert requirement.organization is True

    # an organization cannot be TRUE for any of these fields
    assert (
        any([getattr(requirement, field) for field in non_organization_fields]) is False
    )
    assert requirement_model.objects.count() == 2
    assert requirement_category_model.objects.count() == 2
    assert reference_model.objects.exists() is True

    assert "control_requirement_id" in new_df_columns
    assert "test_guidance" in new_df_columns


@pytest.mark.django_db
def test_source_table_import_management_command(caplog):
    call_command("import_source_table")

    requirement_model = apps.get_model("requirements", "Requirement")
    reference_model = apps.get_model("requirements", "Reference")

    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].message == "Successfully imported source table."

    assert requirement_model.objects.count() > 10
    assert reference_model.objects.count() > 100
