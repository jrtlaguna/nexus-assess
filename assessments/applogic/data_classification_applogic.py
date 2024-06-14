from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


def get_data_classification_fields():
    """This returns a list of tuple of (field_name, label) which is a representation
    of the data_classification JSONField data.

    This defines what fields are expected of the JSONField and is used in other validations.
    """
    fields = [
        (
            "data_classification_secret",
            _(
                mark_safe(
                    """<p><b>Secret</b></p>
            <ul>
            <li>Highly sensitive data intended for limited, specific use by a workgroup, department, or group of individuals with a legitimate need-to-know.</li>
            <li>Explicit authorization by the Data Steward is required for access because of legal, contractual, privacy, or other constraints. The Company is contractually obligated to keep them secret.</li>
            <li>They are critical to the Company’s ability to perform one of its essential business functions and cannot be replaced easily with backup copies.</li>
            <li>Leakage of this information can cause substantial damage to the Company.</li>
            </ul>
        """
                )
            ),
        ),
        (
            "data_classification_restricted",
            _(
                mark_safe(
                    """<p><b>Restricted</b></p>
            <ul>
            <li>Data that must be protected from unauthorized access to safeguard the privacy or security of an individual or organization.</li>
            <li>Not available to the public, and protection is required by the data owner or other confidentiality and may be required by federal or state law or regulation.</li>
            <li>The loss of their confidentiality, integrity, or availability could cause harm to the Company but not as severe as with Secret Data.</li>
            <li>They identify an individual and would customarily be shared only with the individual’s family, doctor, lawyer, or accountant.</li>
            <li>Disclosure is limited to individuals on a need-to-know basis. They could be exploited for criminal or other wrongful purposes, and the Company is obligated by federal or state law or regulation to keep them confidential.</li>
            </ul>
        """
                )
            ),
        ),
        (
            "data_classification_internal",
            _(
                mark_safe(
                    "<p><b>Internal</b></p><p>Information that must be guarded due to proprietary, ethical, or privacy considerations and must be protected from unauthorized access, modification, transmission, storage or other use. This classification applies even though there may not be a civil statute requiring this protection. Internal Data is information that is restricted to personnel who have a legitimate reason to access it.</p>"
                )
            ),
        ),
        (
            "data_classification_public",
            _(
                mark_safe(
                    "<p><b>Public</b></p><p>Information that may or must be open to the general public. It is defined as information with no existing local, national, or international legal restrictions on access or usage. Public data, while subject to disclosure rules, is available to all employees and all individuals or entities external to the corporation.</p>"
                )
            ),
        ),
    ]

    return fields


def get_default_data_classification_json_value():
    """Converts the fields defined in get_data_classification_fields() and converts it into a DICT
    and assigns False as the default value for each boolean field/key and an empty string
    for each textfield field/key.
    """
    return {field[0]: False for field in get_data_classification_fields()}


def validate_data_classification_json(value):
    """Validates the value such that it contains only the expected fields for the data_classification JSONField.
    Also validates that the value for each key is a boolean, and only one key is True.

    Args:
        value (dict): dict to validate against expected values for the CCA data_classification field

    Raises:
        ValidationError: Raises ValidationError if there are invalid keys or invalid values in the dict
    """
    allowed_keys = get_default_data_classification_json_value().keys()

    if not isinstance(value, dict):
        raise ValidationError("Invalid JSON. Must be a dictionary.")

    missing = [key for key in allowed_keys if key not in value]
    if missing:
        raise ValidationError(
            f"Data is missing the following fields: {', '.join(missing)}"
        )

    true_count = 0
    errors = []
    for key, val in value.items():
        if key not in allowed_keys:
            errors.append(
                f"Invalid key: {key}. Only {', '.join(allowed_keys)} are allowed."
            )
        else:
            if not isinstance(val, bool):
                errors.append(
                    f"Invalid value for key {key}. Only boolean values are allowed."
                )

            if isinstance(val, bool) and val is True:
                true_count += 1

    if true_count > 1:
        errors.append("Only 1 Data Classification should be selected.")

    if errors:
        raise ValidationError(errors)


def convert_data_classification_fields_to_json(cleaned_data):
    """Util to convert a form's cleaned_data into a valid dict to use for the data_classification JSONField

    Args:
        cleaned_data (dict): data from a form cleaned_data or any dict

    Returns:
        dict: a dict object that contains only valid keys for the CCA data_classification field
    """
    return {
        key: cleaned_data[key]
        for key in get_default_data_classification_json_value().keys()
        if key in cleaned_data
    }
