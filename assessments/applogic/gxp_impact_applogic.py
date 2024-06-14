from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


def get_gxp_impact_fields(without_comments=False):
    """This returns a list of tuple of (field_name, label) which is a representation
    of the gxp_impact JSONField data.

    This defines what fields are expected of the JSONField and is used in other validations.
    """
    fields = [
        (
            "is_solution_used_for_product_quality_control",
            _(
                mark_safe(
                    """<p>1. Is the solution used for any of the following:</p>
                <ul>
                <li>Product Quality Control</li>
                <li>Used to monitor, control, or supervise:
                    <ul>
                    <li>Packaging and labeling operations</li>
                    <li>Production processes and/or materials</li>
                    <li>GMP facilities/environments or services</li>
                    <li>Commercial manufacturing materials or intermediates supply chain</li>
                    </ul>
                </li>
                <li>As a process control Solution that may control or manipulate the process in such a way to affect drug product quality without independent verification of the control Solution performance? (PLCs, DCS, loop controllers, etc.)</li>
                </ul>
        """
                )
            ),
        ),
        (
            "is_solution_used_for_product_quality_control_comment",
            _("Comments (optional)"),
        ),
        (
            "is_solution_part_of_batch_record",
            _(
                mark_safe(
                    "<p>2. Is the data from the solution recorded as part of the batch record or lot release and/or directly impacts the ability to recall drug product?</p>"
                )
            ),
        ),
        ("is_solution_part_of_batch_record_comment", _("Comments (optional)")),
        (
            "is_impacted_by_gmp_global_regulations",
            _(
                mark_safe(
                    "<p>3. Is this solution impacted by any GMP global regulations that require a company to maintain certain records and submit specific information to the agency as part of compliance (predicate rules)?</p>"
                )
            ),
        ),
        ("is_impacted_by_gmp_global_regulations_comment", _("Comments (optional)")),
        (
            "is_impacted_by_gcp_global_regulations",
            _(
                mark_safe(
                    "<p>4. Is this solution impacted by any GCP global regulations that require a company to maintain certain records and submit specific information to the agency as part of compliance (predicate rules)? Record the regulation(s) in Comments.</p>"
                )
            ),
        ),
        ("is_impacted_by_gcp_global_regulations_comment", _("Comments (optional)")),
        (
            "is_solution_used_to_design_discover_products",
            _(
                mark_safe(
                    """<p>5. Is the solution used for any of the following:</p>
                <ul>
                <li>Used to design, conduct, perform, monitor, audit, record, analyze, and report information from a clinical or animal study?</li>
                <li>Used to discover or verify the clinical, pharmacological and/or other pharmacodynamic effects of an investigational product(s), and/or to identify any adverse reactions to an investigational product(s), and/or to study absorption, distribution, metabolism, and excretion of an investigational product(s) with the object of ascertaining its safety and/or efficacy?</li>
                </ul>
        """
                )
            ),
        ),
        (
            "is_solution_used_to_design_discover_products_comment",
            _("Comments (optional)"),
        ),
        (
            "is_impacted_by_glp_global_regulations",
            _(
                mark_safe(
                    "<p>6. Is this solution impacted by any GLP global regulations that require a company to maintain certain records and submit specific information to the agency as part of compliance (predicate rules)? Record the regulation(s) in Comments.</p>"
                )
            ),
        ),
        ("is_impacted_by_glp_global_regulations_comment", _("Comments (optional)")),
        (
            "is_solution_used_to_collect_and_process_data",
            _(
                mark_safe(
                    """<p>7. Is the solution used for any of the following:</p>
                <ul>
                <li>Used to collect, store, process or transmit patient or data subject original documents, data, and records?</li>
                <li>Used to plan, perform, monitor, record, archive and report non-clinical health and safety data within a laboratory condition/environment to obtain data on its properties or safety?</li>
                </ul>
        """
                )
            ),
        ),
        (
            "is_solution_used_to_collect_and_process_data_comment",
            _("Comments (optional)"),
        ),
        (
            "is_solution_used_for_post_marketing_commitment",
            _(
                mark_safe(
                    "<p>8. Solution is used to design, conduct, perform, monitor, audit, record, analyze, and report information from a clinical or post-marketing commitment?</p>"
                )
            ),
        ),
        (
            "is_solution_used_for_post_marketing_commitment_comment",
            _("Comments (optional)"),
        ),
        (
            "is_solution_used_to_monitor_and_report_source_data",
            _(
                mark_safe(
                    "<p>9. Solution is used to monitor, audit, record, analyze, and report source data (e.g., letters, emails, records of telephone calls, which include details of an event)?</p>"
                )
            ),
        ),
        (
            "is_solution_used_to_monitor_and_report_source_data_comment",
            _("Comments (optional)"),
        ),
        (
            "is_solution_externally_facing_tool",
            _(
                mark_safe(
                    "<p>10. Solution is an externally facing tool (e.g., web sites/digital media site or platform) that could have the potential to generate AE data?</p>"
                )
            ),
        ),
        ("is_solution_externally_facing_tool_comment", _("Comments (optional)")),
        (
            "is_solution_used_to_make_quality_related_decisions",
            _(
                mark_safe(
                    "<p>11. Is the Solution used to create, process, store, hold, manipulate, report data used to make quality related decisions (e.g., Product Reviews, Training Records, Complaints Records, etc.)?</p>"
                )
            ),
        ),
        (
            "is_solution_used_to_make_quality_related_decisions_comment",
            _("Comments (optional)"),
        ),
        (
            "is_solution_used_to_support_gxp_processes",
            _(
                mark_safe(
                    "<p>12. Is the Solution used to provide support to GxP processes and/or systems?</p>"
                )
            ),
        ),
        ("is_solution_used_to_support_gxp_processes_comment", _("Comments (optional)")),
    ]

    if without_comments:
        return [field for field in fields if not field[0].endswith("_comment")]
    return fields


def get_default_gxp_impact_json_value():
    """Converts the fields defined in get_gxp_impact_fields() and converts it into a DICT
    and assigns False as the default value for each boolean field/key and an empty string
    for each textfield field/key.
    """
    return {
        field[0]: "" if field[0].endswith("_comment") else None
        for field in get_gxp_impact_fields()
    }


def validate_gxp_impact_json(value):
    """Validates the value such that it contains only the expected fields for the gxp_impact JSONField.
    Also validates the the value for each key is a boolean.

    Args:
        value (dict): dict to validate against expected values for the CCA gxp_impact field

    Raises:
        ValidationError: Raises ValidationError if there are invalid keys or invalid value in the dict
    """
    allowed_keys = get_default_gxp_impact_json_value().keys()
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


def convert_gxp_impact_fields_to_json(cleaned_data):
    """Util to convert a form's cleaned_data into a valid dict to use for the gxp_impact JSONField

    Args:
        cleaned_data (dict): data from a form cleaned_data or any dict

    Returns:
        dict: a dict object that contains only valid keys for the CCA gxp_impact field
    """
    return {
        key: cleaned_data[key]
        for key in get_default_gxp_impact_json_value().keys()
        if key in cleaned_data
    }


def get_gmp_related_fields():
    return [
        "is_solution_used_for_product_quality_control",
        "is_solution_part_of_batch_record",
        "is_impacted_by_gmp_global_regulations",
    ]


def get_gcp_related_fields():
    return [
        "is_impacted_by_gcp_global_regulations",
        "is_solution_used_to_design_discover_products",
    ]


def get_glp_related_fields():
    return [
        "is_impacted_by_glp_global_regulations",
        "is_solution_used_to_collect_and_process_data",
    ]


def get_gvp_related_fields():
    return [
        "is_solution_used_for_post_marketing_commitment",
        "is_solution_used_to_monitor_and_report_source_data",
        "is_solution_externally_facing_tool",
    ]


def get_gxp_indirect_related_fields():
    return [
        "is_solution_used_to_make_quality_related_decisions",
        "is_solution_used_to_support_gxp_processes",
    ]
