from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


def get_business_impact_fields(without_comments=False):
    """This returns a list of tuple of (field_name, label) which is a representation
    of the business_impact JSONField data.

    This defines what fields are expected of the JSONField and is used in other validations.
    """
    fields = [
        (
            "business_impact_high",
            _(
                mark_safe(
                    """<p><strong>High</strong> <em>(Patient Safety)</em></p>
            <ul>
            <li>Risk to patient safety (GxP)</li>
            <li>Serious disruption of business with no compensating manual processes available.</li>
            </ul>
        """
                )
            ),
        ),
        (
            "business_impact_medium",
            _(
                mark_safe(
                    """<p><strong>Medium</strong> <em>(Business Mission Critical)</em></p>
            <p>(a) Revenue impacted</p>
            <p>(b) Negative customer satisfaction</p>
            <p>(c) Compliance violation (not Patient safety) and/or</p>
            <p>(d) Damage to organization’s reputation</p>
        """
                )
            ),
        ),
        (
            "business_impact_low",
            _(
                mark_safe(
                    """<p><strong>Low</strong> <em>(Business Supporting)</em></p>
            <ul>
            <li>Employee productivity degradation</li>
            </ul>
        """
                )
            ),
        ),
        ("business_impact_comment", _("Comments (optional)")),
    ]

    if without_comments:
        return [field for field in fields if not field[0].endswith("_comment")]
    return fields


def get_default_business_impact_json_value():
    """Converts the fields defined in get_business_impact_fields() and converts it into a DICT
    and assigns False as the default value for each boolean field/key and an empty string
    for each textfield field/key.
    """
    return {
        field[0]: "" if field[0].endswith("_comment") else False
        for field in get_business_impact_fields()
    }


def validate_business_impact_json(value):
    """Validates the value such that it contains only the expected fields for the business_impact JSONField.
    Also validates the the value for each key is a boolean.

    Args:
        value (dict): dict to validate against expected values for the CCA business_impact field

    Raises:
        ValidationError: Raises ValidationError if there are invalid keys or invalid value in the dict
    """
    allowed_keys = get_default_business_impact_json_value().keys()
    boolean_fields = [key for key in allowed_keys if not key.endswith("_comment")]

    if not isinstance(value, dict):
        raise ValidationError("Invalid JSON. Must be a dictionary.")

    missing = [key for key in allowed_keys if key not in value]
    if missing:
        raise ValidationError(
            f"Data is missing the following fields: {','.join(missing)}"
        )

    true_count = 0
    errors = []
    for key, val in value.items():
        if key not in allowed_keys:
            errors.append(
                f"Invalid key: {key}. Only {','.join(allowed_keys)} are allowed."
            )
        else:
            if key in boolean_fields and not isinstance(val, bool):
                errors.append(
                    f"Invalid value for key {key}. Only boolean values are allowed."
                )

            if key in boolean_fields and isinstance(val, bool) and val is True:
                true_count += 1

    if true_count > 1:
        errors.append("Only 1 Business Impact should be selected.")

    if errors:
        raise ValidationError(errors)


def convert_business_impact_fields_to_json(cleaned_data):
    """Util to convert a form's cleaned_data into a valid dict to use for the business_impact JSONField

    Args:
        cleaned_data (dict): data from a form cleaned_data or any dict

    Returns:
        dict: a dict object that contains only valid keys for the CCA business_impact field
    """
    return {
        key: cleaned_data[key]
        for key in get_default_business_impact_json_value().keys()
        if key in cleaned_data
    }
