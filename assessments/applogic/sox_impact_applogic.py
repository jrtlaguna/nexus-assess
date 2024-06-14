from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


def get_sox_impact_fields(without_comments=False):
    """This returns a list of tuple of (field_name, label) which is a representation
    of the sox_impact JSONField data.

    This defines what fields are expected of the JSONField and is used in other validations.
    """
    fields = [
        (
            "is_solution_used_for_material_financial_data",
            _(
                mark_safe(
                    "<p>1. Is this a Solution used for the generation, maintenance, storage or importation of material financial data or financial reports utilized in the financial reporting process?</p>"
                )
            ),
        ),
        (
            "is_solution_used_for_material_financial_data_comment",
            _("Comments (optional)"),
        ),
        (
            "does_solution_provide_access_control_for_financial_systems",
            _(
                mark_safe(
                    "<p>2. Does the solution provide access control for financial systems and integration with other systems?</p>"
                )
            ),
        ),
        (
            "does_solution_provide_access_control_for_financial_systems_comment",
            _("Comments (optional)"),
        ),
        (
            "does_system_feed_information_to_from_sox_system",
            _(
                mark_safe(
                    "<p>3. Does the system feed information, or is it fed information from another in-scope SOX system?</p>"
                )
            ),
        ),
        (
            "does_system_feed_information_to_from_sox_system_comment",
            _("Comments (optional)"),
        ),
    ]

    if without_comments:
        return [field for field in fields if not field[0].endswith("_comment")]
    return fields


def get_default_sox_impact_json_value():
    """Converts the fields defined in get_sox_impact_fields() and converts it into a DICT
    and assigns False as the default value for each boolean field/key and an empty string
    for each textfield field/key.
    """
    return {
        field[0]: "" if field[0].endswith("_comment") else None
        for field in get_sox_impact_fields()
    }


def validate_sox_impact_json(value):
    """Validates the value such that it contains only the expected fields for the sox_impact JSONField.
    Also validates the the value for each key is a boolean.

    Args:
        value (dict): dict to validate against expected values for the CCA sox_impact field

    Raises:
        ValidationError: Raises ValidationError if there are invalid keys or invalid value in the dict
    """
    allowed_keys = get_default_sox_impact_json_value().keys()
    boolean_fields = [key for key in allowed_keys if not key.endswith("_comment")]

    if not isinstance(value, dict):
        raise ValidationError("Invalid JSON. Must be a dictionary.")

    missing = [key for key in allowed_keys if key not in value]
    if missing:
        raise ValidationError(
            f"Data is missing the following fields: {','.join(missing)}"
        )

    errors = []
    for key, val in value.items():
        if key not in allowed_keys:
            errors.append(
                f"Invalid key: {key}. Only {','.join(allowed_keys)} are allowed."
            )
        else:
            if key in boolean_fields and val is not None and not isinstance(val, bool):
                errors.append(
                    f"Invalid value for key {key}. Only boolean or None values are allowed."
                )

    if errors:
        raise ValidationError(errors)


def convert_sox_impact_fields_to_json(cleaned_data):
    """Util to convert a form's cleaned_data into a valid dict to use for the sox_impact JSONField

    Args:
        cleaned_data (dict): data from a form cleaned_data or any dict

    Returns:
        dict: a dict object that contains only valid keys for the CCA sox_impact field
    """
    return {
        key: cleaned_data[key]
        for key in get_default_sox_impact_json_value().keys()
        if key in cleaned_data
    }
