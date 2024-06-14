from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from . import (
    business_impact_applogic,
    data_classification_applogic,
    gxp_eres_applogic,
    gxp_impact_applogic,
    privacy_impact_applogic,
    sox_impact_applogic,
)


def get_summary_fields(grouped=False):
    """This returns a list of tuple of (field_name, label) which is a representation
    of the summary JSONField data.

    This defines what fields are expected of the JSONField and is used in other validations.
    """
    grouped_summary_fields = [
        (
            ("summary_regulatory_gxp_impact_gmp", _(mark_safe("<p>GMP</p>"))),
            ("summary_regulatory_gxp_impact_gcp", _(mark_safe("<p>GCP</p>"))),
            ("summary_regulatory_gxp_impact_glp", _(mark_safe("<p>GLP</p>"))),
            ("summary_regulatory_gxp_impact_gvp", _(mark_safe("<p>GVP</p>"))),
            (
                "summary_regulatory_gxp_impact_gxp_indirect",
                _(mark_safe("<p>GxP Indirect</p>")),
            ),
            ("summary_regulatory_gxp_impact_non_gxp", _(mark_safe("<p>Non-GxP</p>"))),
        ),
        (
            ("summary_regulatory_sox_impact_sox", _(mark_safe("<p>SOX</p>"))),
            ("summary_regulatory_sox_impact_non_sox", _(mark_safe("<p>Non-SOX</p>"))),
        ),
        (
            ("summary_regulatory_gxp_eres_er", _(mark_safe("<p>ER</p>"))),
            ("summary_regulatory_gxp_eres_es", _(mark_safe("<p>ES</p>"))),
            (
                "summary_regulatory_gxp_eres_non_eres",
                _(mark_safe("<p>Non-ERES</p>")),
            ),
        ),
        (
            (
                "summary_regulatory_privacy_impact_high_privacy",
                _(mark_safe("<p>High Privacy</p>")),
            ),
            (
                "summary_regulatory_privacy_impact_medium_privacy",
                _(mark_safe("<p>Medium Privacy</p>")),
            ),
            (
                "summary_regulatory_privacy_impact_low_privacy",
                _(mark_safe("<p>Low Privacy</p>")),
            ),
            (
                "summary_regulatory_privacy_impact_no_privacy",
                _(mark_safe("<p>No Privacy</p>")),
            ),
        ),
        (
            (
                "summary_regulatory_impact_administrative_audit_trail_review",
                _(mark_safe("<p>Administrative Audit Trail Review</p>")),
            ),
            (
                "summary_regulatory_impact_operational_audit_trail_review",
                _(mark_safe("<p>Operational Audit Trail Review</p>")),
            ),
        ),
        (
            (
                "summary_data_classification_secret",
                _(mark_safe("<p>Secret Data Classification</p>")),
            ),
            (
                "summary_data_classification_restricted",
                _(mark_safe("<p>Restricted Data Classification</p>")),
            ),
            (
                "summary_data_classification_internal",
                _(mark_safe("<p>Internal Data Classification</p>")),
            ),
            (
                "summary_data_classification_public",
                _(mark_safe("<p>Public Data Classification</p>")),
            ),
        ),
        (
            (
                "summary_business_impact_high",
                _(mark_safe("<p>High Business Impact</p>")),
            ),
            (
                "summary_business_impact_medium",
                _(mark_safe("<p>Medium Business Impact</p>")),
            ),
            ("summary_business_impact_low", _(mark_safe("<p>Low Business Impact</p>"))),
        ),
    ]

    if grouped:
        return grouped_summary_fields
    return [item for group in grouped_summary_fields for item in group]


def get_default_summary_json_value():
    """Converts the fields defined in get_summary_fields() and converts it into a DICT
    and assigns False as the default value for each field/key
    """
    return {field[0]: False for field in get_summary_fields()}


def validate_summary_json(value):
    """Validates the value such that it contains only the expected fields for the summary JSONField.
    Also validates the the value for each key is a boolean.

    Args:
        value (dict): dict to validate against expected values for the CCA summary field

    Raises:
        ValidationError: Raises ValidationError if there are invalid keys or invalid value in the dict
    """
    allowed_keys = get_default_summary_json_value().keys()

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
            if not isinstance(val, bool):
                errors.append(
                    f"Invalid value for key {key}. Only boolean values are allowed."
                )

    if errors:
        raise ValidationError(errors)


def convert_summary_fields_to_json(cleaned_data):
    """Util to convert a form's cleaned_data into a valid dict to use for the summary JSONField

    Args:
        cleaned_data (dict): data from a form cleaned_data or any dict

    Returns:
        dict: a dict object that contains only valid keys for the CCA summary field
    """
    return {
        key: cleaned_data[key]
        for key in get_default_summary_json_value().keys()
        if key in cleaned_data
    }


def get_gxp_impact_summary(summary, data_set):
    related_fields = [
        field[0]
        for field in gxp_impact_applogic.get_gxp_impact_fields(without_comments=True)
    ]

    is_non_gxp = all(not data_set.get(question, True) for question in related_fields)
    summary["summary_regulatory_gxp_impact_non_gxp"] = is_non_gxp

    if not is_non_gxp:
        # if solution is gxp, check individual sections
        summary["summary_regulatory_gxp_impact_gmp"] = any(
            data_set.get(question, False)
            for question in gxp_impact_applogic.get_gmp_related_fields()
        )
        summary["summary_regulatory_gxp_impact_gcp"] = any(
            data_set.get(question, False)
            for question in gxp_impact_applogic.get_gcp_related_fields()
        )
        summary["summary_regulatory_gxp_impact_glp"] = any(
            data_set.get(question, False)
            for question in gxp_impact_applogic.get_glp_related_fields()
        )
        summary["summary_regulatory_gxp_impact_gvp"] = any(
            data_set.get(question, False)
            for question in gxp_impact_applogic.get_gvp_related_fields()
        )
        summary["summary_regulatory_gxp_impact_gxp_indirect"] = any(
            data_set.get(question, False)
            for question in gxp_impact_applogic.get_gxp_indirect_related_fields()
        )

    return summary


def get_sox_impact_summary(summary, data_set):
    related_fields = [
        field[0]
        for field in sox_impact_applogic.get_sox_impact_fields(without_comments=True)
    ]

    is_sox_impact = any(data_set.get(question, False) for question in related_fields)
    summary["summary_regulatory_sox_impact_sox"] = is_sox_impact
    summary["summary_regulatory_sox_impact_non_sox"] = not is_sox_impact

    return summary


def get_gxp_eres_summary(summary, data_set):
    related_fields = [
        field[0]
        for field in gxp_eres_applogic.get_gxp_eres_fields(without_comments=True)
    ]

    is_non_eres = all(not data_set.get(question, True) for question in related_fields)
    summary["summary_regulatory_gxp_eres_non_eres"] = is_non_eres

    if not is_non_eres:
        # if solution is gxp eres, check individual sections
        summary["summary_regulatory_gxp_eres_er"] = any(
            data_set.get(question, False)
            for question in gxp_eres_applogic.get_gxp_er_related_fields()
        )
        summary["summary_regulatory_gxp_eres_es"] = any(
            data_set.get(question, False)
            for question in gxp_eres_applogic.get_gxp_es_related_fields()
        )

    return summary


def get_privacy_impact_summary(summary, data_set):
    related_fields = [
        field[0]
        for field in privacy_impact_applogic.get_privacy_impact_fields(
            without_comments=True
        )
    ]

    q1 = data_set[related_fields[0]]
    q2 = data_set[related_fields[1]]
    summary["summary_regulatory_privacy_impact_high_privacy"] = (q1 and q2) or (
        q1 and not q2
    )
    summary["summary_regulatory_privacy_impact_medium_privacy"] = q2 and not q1
    # no triggers for this
    # summary["summary_regulatory_privacy_impact_low_privacy"] = q1 and not q2
    summary["summary_regulatory_privacy_impact_no_privacy"] = not q1 and not q2

    return summary


def get_data_classification_summary(summary, data_set):
    related_fields = [
        field[0]
        for field in data_classification_applogic.get_data_classification_fields()
    ]

    for field in related_fields:
        summary[f"summary_{field}"] = data_set[field]

    return summary


def get_business_impact_summary(summary, data_set):
    related_fields = [
        field[0]
        for field in business_impact_applogic.get_business_impact_fields(
            without_comments=True
        )
    ]

    for field in related_fields:
        summary[f"summary_{field}"] = data_set[field]

    return summary


def get_audit_trail_summary(summary):
    operational_related_fields = [
        "summary_regulatory_gxp_impact_gmp",
        "summary_regulatory_gxp_impact_gcp",
        "summary_regulatory_gxp_impact_glp",
        "summary_regulatory_gxp_impact_gvp",
    ]
    admin_related_fields = operational_related_fields + [
        "summary_regulatory_gxp_impact_gxp_indirect"
    ]

    summary["summary_regulatory_impact_administrative_audit_trail_review"] = any(
        summary.get(field, False) for field in admin_related_fields
    )
    summary["summary_regulatory_impact_operational_audit_trail_review"] = any(
        summary.get(field, False) for field in operational_related_fields
    )

    return summary


def calculate_summary(cca_data):
    """Calculates summary values based on cca_data

    Args:
        cca_data (dict): a dict of CCA questionnaire responses

    Returns:
        dict: a dict of summary fields with corresponding calculated value

    Execption:
        KeyError - Naturally raises KeyError if there is a missmatch of cca_data fields and summary fields
    """
    summary = get_default_summary_json_value()

    summary = get_gxp_impact_summary(summary, cca_data["gxp_impact"])
    summary = get_sox_impact_summary(summary, cca_data["sox_impact"])
    summary = get_gxp_eres_summary(summary, cca_data["gxp_eres"])
    summary = get_privacy_impact_summary(summary, cca_data["privacy_impact"])
    summary = get_data_classification_summary(summary, cca_data["data_classification"])
    summary = get_business_impact_summary(summary, cca_data["business_impact"])

    # NOTE: Audit Trail is calculated based on summary gxp, so this needs to be last
    summary = get_audit_trail_summary(summary)

    return summary
