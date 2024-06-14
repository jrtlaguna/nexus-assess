from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .data_classification_applogic import get_data_classification_fields


def get_rating_fields():
    """This returns a list of tuple of (field_name, label) which is a representation
    of the rating JSONField data.

    This defines what fields are expected of the JSONField and is used in other validations.
    """
    return [
        (
            "rating_significant",
            _(
                mark_safe(
                    """<p><strong>Significant</strong></p>
            <ul>
            <li><strong>Regulatory:</strong> GxP-Direct Impact OR</li>
            <li><strong>Data Classification:</strong> SECRET OR</li>
            </ul>
        """
                )
            ),
        ),
        (
            "rating_moderate",
            _(
                mark_safe(
                    """<p><strong>Moderate</strong></p>
            <ul>
            <li><strong>Regulatory:</strong> GxP-Indirect Impact, SOX, High or Medium Privacy Impact etc. OR</li>
            <li><strong>Data Classification:</strong> INTERNAL OR RESTRICTED OR</li>
            <li><strong>Business Impact:</strong> High</li>
            </ul>
        """
                )
            ),
        ),
        (
            "rating_minimal",
            _(
                mark_safe(
                    """<p><strong>Minimal</strong></p>
            <ul>
            <li><strong>Regulatory:</strong> Non-GxP Impact, Low Privacy Impact, non-SOX OR</li>
            <li><strong>Data Classification:</strong> PUBLIC OR</li>
            <li><strong>Business Impact:</strong> Medium</li>
            </ul>
        """
                )
            ),
        ),
        (
            "rating_no_compliance_risk",
            _(
                mark_safe(
                    """<p><strong>No Compliance Risk</strong></p>
            <ul>
            <li><strong>Regulatory:</strong> Non-GxP Impact, No Privacy Impact, non-SOX AND</li>
            <li><strong>Business Impact:</strong> Low</li>
            </ul>
            <p>Provide justification in the comment section when No Compliance Risk is selected.</p>
        """
                )
            ),
        ),
        ("rating_comment", _("Comments (optional)")),
    ]


def get_default_rating_json_value():
    """Converts the fields defined in get_rating_fields() and converts it into a DICT
    and assigns False as the default value for each boolean field/key and an empty string
    for each textfield field/key.
    """
    return {
        field[0]: "" if field[0].endswith("_comment") else False
        for field in get_rating_fields()
    }


def validate_rating_json(value):
    """Validates the value such that it contains only the expected fields for the rating JSONField.
    Also validates the the value for each key is a boolean.

    Args:
        value (dict): dict to validate against expected values for the CCA rating field

    Raises:
        ValidationError: Raises ValidationError if there are invalid keys or invalid value in the dict
    """
    allowed_keys = get_default_rating_json_value().keys()
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
            if key in boolean_fields and not isinstance(val, bool):
                errors.append(
                    f"Invalid value for key {key}. Only boolean values are allowed."
                )

    if errors:
        raise ValidationError(errors)


def convert_rating_fields_to_json(cleaned_data):
    """Util to convert a form's cleaned_data into a valid dict to use for the rating JSONField

    Args:
        cleaned_data (dict): data from a form cleaned_data or any dict

    Returns:
        dict: a dict object that contains only valid keys for the CCA rating field
    """
    return {
        key: cleaned_data[key]
        for key in get_default_rating_json_value().keys()
        if key in cleaned_data
    }


def calculate_rating(summary_data):
    """Calculates rating values based on summary

    Args:
        summary_data (dict): a dict of summary values from cca questionnaire responses

    Returns:
        dict: a dict of rating fields with corresponding calculated value

    Execption:
        KeyError - Naturally raises KeyError if there is a missmatch of cca_data fields and summary fields
    """

    rating = get_default_rating_json_value()
    no_business_impact_checked = all(
        not summary_data[field]
        for field in [
            "summary_business_impact_high",
            "summary_business_impact_medium",
            "summary_business_impact_low",
        ]
    )
    no_data_classification_cheked = all(
        not summary_data[field]
        for field in [
            "summary_data_classification_public",
            "summary_data_classification_internal",
            "summary_data_classification_restricted",
            "summary_data_classification_secret",
        ]
    )

    if (
        summary_data["summary_regulatory_gxp_impact_non_gxp"]
        and summary_data["summary_regulatory_privacy_impact_no_privacy"]
        and summary_data["summary_regulatory_sox_impact_non_sox"]
        and (summary_data["summary_business_impact_low"] or no_business_impact_checked)
        and no_data_classification_cheked
    ):
        rating["rating_no_compliance_risk"] = True
    elif (
        summary_data["summary_regulatory_gxp_impact_gmp"]
        or summary_data["summary_regulatory_gxp_impact_gcp"]
        or summary_data["summary_regulatory_gxp_impact_glp"]
        or summary_data["summary_regulatory_gxp_impact_gvp"]
        or summary_data["summary_data_classification_secret"]
    ):
        rating["rating_significant"] = True

    elif (
        summary_data["summary_regulatory_gxp_impact_gxp_indirect"]
        or summary_data["summary_regulatory_sox_impact_sox"]
        or summary_data["summary_regulatory_privacy_impact_high_privacy"]
        or summary_data["summary_regulatory_privacy_impact_medium_privacy"]
        or summary_data["summary_data_classification_internal"]
        or summary_data["summary_data_classification_restricted"]
        or summary_data["summary_business_impact_high"]
    ):
        rating["rating_moderate"] = True
    elif (
        summary_data["summary_regulatory_gxp_impact_non_gxp"]
        or summary_data["summary_regulatory_privacy_impact_low_privacy"]
        or summary_data["summary_regulatory_sox_impact_non_sox"]
        or summary_data["summary_data_classification_public"]
        or summary_data["summary_business_impact_medium"]
    ):
        rating["rating_minimal"] = True
    else:
        # Ideally, if conditions don't meet the above, the solution should be considered
        # No Compliance Risk. But note that there are supposedly conditions set for it
        # to be considered no risk, see below:
        #
        # Regulatory: Non-GxP Impact, No Privacy Impact, non-SOX AND
        # Business Impact: Low
        rating["rating_no_compliance_risk"] = True

    return rating
