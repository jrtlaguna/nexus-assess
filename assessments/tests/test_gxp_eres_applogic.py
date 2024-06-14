import pytest

from django.core.exceptions import ValidationError

from ..applogic.gxp_eres_applogic import (
    convert_gxp_eres_fields_to_json,
    get_default_gxp_eres_json_value,
    get_gxp_er_related_fields,
    get_gxp_eres_fields,
    get_gxp_es_related_fields,
    validate_gxp_eres_json,
)


def test_get_gxp_eres_fields():
    fields = get_gxp_eres_fields()

    # Check if the function returns a list
    assert isinstance(fields, list)

    # Check if each element in the list is a tuple with two elements
    for field in fields:
        assert isinstance(field, tuple)
        assert len(field) == 2

    # The important thing to check here is the field names, the label can be anything as long as the field names don't change
    assert (
        fields[0][0]
        == "does_solution_create_records_in_electronic_form_required_by_gxp_regulation"
    )
    assert (
        fields[1][0]
        == "does_solution_create_records_in_electronic_form_required_by_gxp_regulation_comment"
    )
    assert fields[2][0] == "does_solution_employ_electorinic_signatures"
    assert fields[3][0] == "does_solution_employ_electorinic_signatures_comment"


def test_get_default_gxp_eres_json_value():
    default_values = get_default_gxp_eres_json_value()

    # Check if the function returns a dictionary
    assert isinstance(default_values, dict)

    # Check if each field is assigned the correct default value
    for field, value in default_values.items():
        if field.endswith("_comment"):
            assert value == ""
        else:
            assert value is None

    # Check if the dictionary has the expected keys from get_gxp_eres_fields
    expected_keys = [field[0] for field in get_gxp_eres_fields()]
    assert set(default_values.keys()) == set(expected_keys)


def test_validate_gxp_eres_json():
    allowed_keys = get_default_gxp_eres_json_value().keys()

    # Test valid input
    valid_input = get_default_gxp_eres_json_value()
    validate_gxp_eres_json(valid_input)  # This should not raise any exception

    # Test invalid input - non-dictionary
    with pytest.raises(ValidationError, match="Invalid JSON. Must be a dictionary."):
        validate_gxp_eres_json("invalid_input")

    # Test invalid input - invalid key
    invalid_input_key = get_default_gxp_eres_json_value()
    invalid_input_key.update({"invalid_key": True})
    with pytest.raises(
        ValidationError,
        match=f"Invalid key: invalid_key. Only {','.join(allowed_keys)} are allowed.",
    ):
        validate_gxp_eres_json(invalid_input_key)

    # Test invalid input - invalid value type for boolean
    invalid_input_value = get_default_gxp_eres_json_value()
    invalid_input_value.update(
        {
            "does_solution_create_records_in_electronic_form_required_by_gxp_regulation": "invalid_value"
        }
    )
    with pytest.raises(
        ValidationError,
        match="Invalid value for key does_solution_create_records_in_electronic_form_required_by_gxp_regulation. Only boolean or None values are allowed.",
    ):
        validate_gxp_eres_json(invalid_input_value)

    # Test input for comment fields - should not throw the same error as boolean
    comment_input_value = get_default_gxp_eres_json_value()
    comment_input_value.update(
        {
            "does_solution_create_records_in_electronic_form_required_by_gxp_regulation_comment": "some value"
        }
    )
    validate_gxp_eres_json(comment_input_value)

    # Test invalid input - missing keys
    invalid_input_missing_keys = get_default_gxp_eres_json_value()
    invalid_input_missing_keys.pop(
        "does_solution_create_records_in_electronic_form_required_by_gxp_regulation"
    )
    with pytest.raises(
        ValidationError,
        match=f"Data is missing the following fields: does_solution_create_records_in_electronic_form_required_by_gxp_regulation",
    ):
        validate_gxp_eres_json(invalid_input_missing_keys)


def test_convert_gxp_eres_fields_to_json():
    # Test valid input
    valid_input = get_default_gxp_eres_json_value()
    result = convert_gxp_eres_fields_to_json(valid_input)
    assert result == valid_input

    # Test invalid input - extra keys
    invalid_input_extra_keys = get_default_gxp_eres_json_value()
    invalid_input_extra_keys.update({"extra_key": True})
    result = convert_gxp_eres_fields_to_json(invalid_input_extra_keys)
    assert result == get_default_gxp_eres_json_value()
    assert "extra_key" not in result

    # Test invalid input - missing keys
    invalid_input_missing_keys = {}
    result = convert_gxp_eres_fields_to_json(invalid_input_missing_keys)
    assert result == {}


def test_get_gxp_er_related_fields():
    result = get_gxp_er_related_fields()
    expected = [
        "does_solution_create_records_in_electronic_form_required_by_gxp_regulation",
    ]
    assert result == expected


def test_get_gxp_es_related_fields():
    result = get_gxp_es_related_fields()
    expected = [
        "does_solution_employ_electorinic_signatures",
    ]
    assert result == expected
