import pytest

from django.core.exceptions import ValidationError

from ..applogic.gxp_impact_applogic import (
    convert_gxp_impact_fields_to_json,
    get_default_gxp_impact_json_value,
    get_gcp_related_fields,
    get_glp_related_fields,
    get_gmp_related_fields,
    get_gvp_related_fields,
    get_gxp_impact_fields,
    get_gxp_indirect_related_fields,
    validate_gxp_impact_json,
)


def test_get_gxp_impact_fields():
    fields = get_gxp_impact_fields()

    # Check if the function returns a list
    assert isinstance(fields, list)

    # Check if each element in the list is a tuple with two elements
    for field in fields:
        assert isinstance(field, tuple)
        assert len(field) == 2

    # The important thing to check here is the field names, the label can be anything as long as the field names don't change
    assert fields[0][0] == "is_solution_used_for_product_quality_control"
    assert fields[1][0] == "is_solution_used_for_product_quality_control_comment"
    assert fields[2][0] == "is_solution_part_of_batch_record"
    assert fields[3][0] == "is_solution_part_of_batch_record_comment"
    assert fields[4][0] == "is_impacted_by_gmp_global_regulations"
    assert fields[5][0] == "is_impacted_by_gmp_global_regulations_comment"
    assert fields[6][0] == "is_impacted_by_gcp_global_regulations"
    assert fields[7][0] == "is_impacted_by_gcp_global_regulations_comment"
    assert fields[8][0] == "is_solution_used_to_design_discover_products"
    assert fields[9][0] == "is_solution_used_to_design_discover_products_comment"
    assert fields[10][0] == "is_impacted_by_glp_global_regulations"
    assert fields[11][0] == "is_impacted_by_glp_global_regulations_comment"
    assert fields[12][0] == "is_solution_used_to_collect_and_process_data"
    assert fields[13][0] == "is_solution_used_to_collect_and_process_data_comment"
    assert fields[14][0] == "is_solution_used_for_post_marketing_commitment"
    assert fields[15][0] == "is_solution_used_for_post_marketing_commitment_comment"
    assert fields[16][0] == "is_solution_used_to_monitor_and_report_source_data"
    assert fields[17][0] == "is_solution_used_to_monitor_and_report_source_data_comment"
    assert fields[18][0] == "is_solution_externally_facing_tool"
    assert fields[19][0] == "is_solution_externally_facing_tool_comment"
    assert fields[20][0] == "is_solution_used_to_make_quality_related_decisions"
    assert fields[21][0] == "is_solution_used_to_make_quality_related_decisions_comment"
    assert fields[22][0] == "is_solution_used_to_support_gxp_processes"
    assert fields[23][0] == "is_solution_used_to_support_gxp_processes_comment"


def test_get_default_gxp_impact_json_value():
    default_values = get_default_gxp_impact_json_value()

    # Check if the function returns a dictionary
    assert isinstance(default_values, dict)

    # Check if each field is assigned the correct default value
    for field, value in default_values.items():
        if field.endswith("_comment"):
            assert value == ""
        else:
            assert value is None

    # Check if the dictionary has the expected keys from get_gxp_impact_fields
    expected_keys = [field[0] for field in get_gxp_impact_fields()]
    assert set(default_values.keys()) == set(expected_keys)


def test_validate_gxp_impact_json():
    allowed_keys = get_default_gxp_impact_json_value().keys()

    # Test valid input
    valid_input = get_default_gxp_impact_json_value()
    validate_gxp_impact_json(valid_input)  # This should not raise any exception

    # Test invalid input - non-dictionary
    with pytest.raises(ValidationError, match="Invalid JSON. Must be a dictionary."):
        validate_gxp_impact_json("invalid_input")

    # Test invalid input - invalid key
    invalid_input_key = get_default_gxp_impact_json_value()
    invalid_input_key.update({"invalid_key": True})
    with pytest.raises(
        ValidationError,
        match=f"Invalid key: invalid_key. Only {','.join(allowed_keys)} are allowed.",
    ):
        validate_gxp_impact_json(invalid_input_key)

    # Test invalid input - invalid value type for boolean
    invalid_input_value = get_default_gxp_impact_json_value()
    invalid_input_value.update(
        {"is_solution_used_for_product_quality_control": "invalid_value"}
    )
    with pytest.raises(
        ValidationError,
        match="Invalid value for key is_solution_used_for_product_quality_control. Only boolean or None values are allowed.",
    ):
        validate_gxp_impact_json(invalid_input_value)

    # Test input for comment fields - should not throw the same error as boolean
    comment_input_value = get_default_gxp_impact_json_value()
    comment_input_value.update(
        {"is_solution_used_for_product_quality_control_comment": "some value"}
    )
    validate_gxp_impact_json(comment_input_value)

    # Test invalid input - missing keys
    invalid_input_missing_keys = get_default_gxp_impact_json_value()
    invalid_input_missing_keys.pop("is_solution_used_for_product_quality_control")
    with pytest.raises(
        ValidationError,
        match=f"Data is missing the following fields: is_solution_used_for_product_quality_control",
    ):
        validate_gxp_impact_json(invalid_input_missing_keys)


def test_convert_gxp_impact_fields_to_json():
    # Test valid input
    valid_input = get_default_gxp_impact_json_value()
    result = convert_gxp_impact_fields_to_json(valid_input)
    assert result == valid_input

    # Test invalid input - extra keys
    invalid_input_extra_keys = get_default_gxp_impact_json_value()
    invalid_input_extra_keys.update({"extra_key": True})
    result = convert_gxp_impact_fields_to_json(invalid_input_extra_keys)
    assert result == get_default_gxp_impact_json_value()
    assert "extra_key" not in result

    # Test invalid input - missing keys
    invalid_input_missing_keys = {}
    result = convert_gxp_impact_fields_to_json(invalid_input_missing_keys)
    assert result == {}


def test_get_gmp_related_fields():
    result = get_gmp_related_fields()
    expected = [
        "is_solution_used_for_product_quality_control",
        "is_solution_part_of_batch_record",
        "is_impacted_by_gmp_global_regulations",
    ]
    assert result == expected


def test_get_gcp_related_fields():
    result = get_gcp_related_fields()
    expected = [
        "is_impacted_by_gcp_global_regulations",
        "is_solution_used_to_design_discover_products",
    ]
    assert result == expected


def test_get_glp_related_fields():
    result = get_glp_related_fields()
    expected = [
        "is_impacted_by_glp_global_regulations",
        "is_solution_used_to_collect_and_process_data",
    ]
    assert result == expected


def test_get_gvp_related_fields():
    result = get_gvp_related_fields()
    expected = [
        "is_solution_used_for_post_marketing_commitment",
        "is_solution_used_to_monitor_and_report_source_data",
        "is_solution_externally_facing_tool",
    ]
    assert result == expected


def test_get_gxp_indirect_related_fields():
    result = get_gxp_indirect_related_fields()
    expected = [
        "is_solution_used_to_make_quality_related_decisions",
        "is_solution_used_to_support_gxp_processes",
    ]
    assert result == expected
