from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


def get_gxp_eres_fields(without_comments=False):
    """This returns a list of tuple of (field_name, label) which is a representation
    of the gxp_eres JSONField data.

    This defines what fields are expected of the JSONField and is used in other validations.
    """
    fields = [
        (
            "does_solution_create_records_in_electronic_form_required_by_gxp_regulation",
            _(
                mark_safe(
                    "<p>1. Does the system create, modify, maintain, archive, retrieve, or transmit records in electronic form that are required by any MD or GxP regulation or that are otherwise submitted to the External Health Authorities (i.e., FDA, EU, etc.)?</p>"
                )
            ),
        ),
        (
            "does_solution_create_records_in_electronic_form_required_by_gxp_regulation_comment",
            _("Comments (optional)"),
        ),
        (
            "does_solution_employ_electorinic_signatures",
            _(
                mark_safe(
                    "<p>2. Does the system employ electronic signatures that are considered the equivalent to handwritten signatures executed on paper?</p>"
                )
            ),
        ),
        (
            "does_solution_employ_electorinic_signatures_comment",
            _("Comments (optional)"),
        ),
    ]

    if without_comments:
        return [field for field in fields if not field[0].endswith("_comment")]
    return fields


def get_default_gxp_eres_json_value():
    """Converts the fields defined in get_gxp_eres_fields() and converts it into a DICT
    and assigns False as the default value for each boolean field/key and an empty string
    for each textfield field/key.
    """
    return {
        field[0]: "" if field[0].endswith("_comment") else None
        for field in get_gxp_eres_fields()
    }


def validate_gxp_eres_json(value):
    """Validates the value such that it contains only the expected fields for the gxp_eres JSONField.
    Also validates the the value for each key is a boolean.

    Args:
        value (dict): dict to validate against expected values for the CCA gxp_eres field

    Raises:
        ValidationError: Raises ValidationError if there are invalid keys or invalid value in the dict
    """
    allowed_keys = get_default_gxp_eres_json_value().keys()
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


def convert_gxp_eres_fields_to_json(cleaned_data):
    """Util to convert a form's cleaned_data into a valid dict to use for the gxp_eres JSONField

    Args:
        cleaned_data (dict): data from a form cleaned_data or any dict

    Returns:
        dict: a dict object that contains only valid keys for the CCA gxp_eres field
    """
    return {
        key: cleaned_data[key]
        for key in get_default_gxp_eres_json_value().keys()
        if key in cleaned_data
    }


def get_gxp_er_related_fields():
    return [
        "does_solution_create_records_in_electronic_form_required_by_gxp_regulation",
    ]


def get_gxp_es_related_fields():
    return [
        "does_solution_employ_electorinic_signatures",
    ]
