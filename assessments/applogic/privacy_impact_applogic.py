from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


def get_privacy_impact_fields(without_comments=False):
    """This returns a list of tuple of (field_name, label) which is a representation
    of the privacy_impact JSONField data.

    This defines what fields are expected of the JSONField and is used in other validations.
    """
    fields = [
        (
            "does_solution_collect_person_information",
            _(
                mark_safe(
                    """<p>1. Does the Solution collect, process, and/or disclose Personal Information (or does not prevent the ability to), directly or through a third party, as defined in the Processing EU Personal Data and/or in the Company standard operating procedure, Processing of European Union Personal Data and Privacy by Design Standard Operating Procedure?</p>
           <p><em>Note: The EU countries are: Austria, Belgium, Bulgaria, Croatia, Republic of Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Poland, Portugal, Romania, Slovakia, Slovenia, Spain, and Sweden.</em></p>
        """
                )
            ),
        ),
        ("does_solution_collect_person_information_comment", _("Comments (optional)")),
        (
            "will_personal_info_collected_be_from_individual_not_in_eu_country",
            _(
                mark_safe(
                    "<p>2. Will the personal information being collected, processed, or disclosed belong to an individual not residing in an EU country?</p>"
                )
            ),
        ),
        (
            "will_personal_info_collected_be_from_individual_not_in_eu_country_comment",
            _("Comments (optional)"),
        ),
    ]

    if without_comments:
        return [field for field in fields if not field[0].endswith("_comment")]
    return fields


def get_default_privacy_impact_json_value():
    """Converts the fields defined in get_privacy_impact_fields() and converts it into a DICT
    and assigns False as the default value for each boolean field/key and an empty string
    for each textfield field/key.
    """
    return {
        field[0]: "" if field[0].endswith("_comment") else None
        for field in get_privacy_impact_fields()
    }


def validate_privacy_impact_json(value):
    """Validates the value such that it contains only the expected fields for the privacy_impact JSONField.
    Also validates the the value for each key is a boolean.

    Args:
        value (dict): dict to validate against expected values for the CCA privacy_impact field

    Raises:
        ValidationError: Raises ValidationError if there are invalid keys or invalid value in the dict
    """
    allowed_keys = get_default_privacy_impact_json_value().keys()
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


def convert_privacy_impact_fields_to_json(cleaned_data):
    """Util to convert a form's cleaned_data into a valid dict to use for the privacy_impact JSONField

    Args:
        cleaned_data (dict): data from a form cleaned_data or any dict

    Returns:
        dict: a dict object that contains only valid keys for the CCA privacy_impact field
    """
    return {
        key: cleaned_data[key]
        for key in get_default_privacy_impact_json_value().keys()
        if key in cleaned_data
    }
