import pytest

from django.core.exceptions import ValidationError

from ..applogic.sox_impact_applogic import (
    convert_sox_impact_fields_to_json,
    get_default_sox_impact_json_value,
    get_sox_impact_fields,
    validate_sox_impact_json,
)


def test_get_sox_impact_fields():
    fields = get_sox_impact_fields()

    # Check if the function returns a list
    assert isinstance(fields, list)

    # Check if each element in the list is a tuple with two elements
    for field in fields:
        assert isinstance(field, tuple)
        assert len(field) == 2

    # The important thing to check here is the field names, the label can be anything as long as the field names don't change
    assert fields[0][0] == "is_solution_used_for_material_financial_data"
    assert fields[1][0] == "is_solution_used_for_material_financial_data_comment"
    assert fields[2][0] == "does_solution_provide_access_control_for_financial_systems"
    assert (
        fields[3][0]
        == "does_solution_provide_access_control_for_financial_systems_comment"
    )
    assert fields[4][0] == "does_system_feed_information_to_from_sox_system"
    assert fields[5][0] == "does_system_feed_information_to_from_sox_system_comment"


def test_get_default_sox_impact_json_value():
    default_values = get_default_sox_impact_json_value()

    # Check if the function returns a dictionary
    assert isinstance(default_values, dict)

    # Check if each field is assigned the correct default value
    for field, value in default_values.items():
        if field.endswith("_comment"):
            assert value == ""
        else:
            assert value is None

    # Check if the dictionary has the expected keys from get_sox_impact_fields
    expected_keys = [field[0] for field in get_sox_impact_fields()]
    assert set(default_values.keys()) == set(expected_keys)


def test_validate_sox_impact_json():
    allowed_keys = get_default_sox_impact_json_value().keys()

    # Test valid input
    valid_input = get_default_sox_impact_json_value()
    validate_sox_impact_json(valid_input)  # This should not raise any exception

    # Test invalid input - non-dictionary
    with pytest.raises(ValidationError, match="Invalid JSON. Must be a dictionary."):
        validate_sox_impact_json("invalid_input")

    # Test invalid input - invalid key
    invalid_input_key = get_default_sox_impact_json_value()
    invalid_input_key.update({"invalid_key": True})
    with pytest.raises(
        ValidationError,
        match=f"Invalid key: invalid_key. Only {','.join(allowed_keys)} are allowed.",
    ):
        validate_sox_impact_json(invalid_input_key)

    # Test invalid input - invalid value type for boolean
    invalid_input_value = get_default_sox_impact_json_value()
    invalid_input_value.update(
        {"is_solution_used_for_material_financial_data": "invalid_value"}
    )
    with pytest.raises(
        ValidationError,
        match="Invalid value for key is_solution_used_for_material_financial_data. Only boolean or None values are allowed.",
    ):
        validate_sox_impact_json(invalid_input_value)

    # Test input for comment fields - should not throw the same error as boolean
    comment_input_value = get_default_sox_impact_json_value()
    comment_input_value.update(
        {"is_solution_used_for_material_financial_data_comment": "some value"}
    )
    validate_sox_impact_json(comment_input_value)

    # Test invalid input - missing keys
    invalid_input_missing_keys = get_default_sox_impact_json_value()
    invalid_input_missing_keys.pop("is_solution_used_for_material_financial_data")
    with pytest.raises(
        ValidationError,
        match=f"Data is missing the following fields: is_solution_used_for_material_financial_data",
    ):
        validate_sox_impact_json(invalid_input_missing_keys)


def test_convert_sox_impact_fields_to_json():
    # Test valid input
    valid_input = get_default_sox_impact_json_value()
    result = convert_sox_impact_fields_to_json(valid_input)
    assert result == valid_input

    # Test invalid input - extra keys
    invalid_input_extra_keys = get_default_sox_impact_json_value()
    invalid_input_extra_keys.update({"extra_key": True})
    result = convert_sox_impact_fields_to_json(invalid_input_extra_keys)
    assert result == get_default_sox_impact_json_value()
    assert "extra_key" not in result

    # Test invalid input - missing keys
    invalid_input_missing_keys = {}
    result = convert_sox_impact_fields_to_json(invalid_input_missing_keys)
    assert result == {}
