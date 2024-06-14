import pytest

from django.core.exceptions import ValidationError

from ..applogic.business_impact_applogic import (
    convert_business_impact_fields_to_json,
    get_business_impact_fields,
    get_default_business_impact_json_value,
    validate_business_impact_json,
)


def test_get_business_impact_fields():
    fields = get_business_impact_fields()

    # Check if the function returns a list
    assert isinstance(fields, list)

    # Check if each element in the list is a tuple with two elements
    for field in fields:
        assert isinstance(field, tuple)
        assert len(field) == 2

    # The important thing to check here is the field names, the label can be anything as long as the field names don't change
    assert fields[0][0] == "business_impact_high"
    assert fields[1][0] == "business_impact_medium"
    assert fields[2][0] == "business_impact_low"
    assert fields[3][0] == "business_impact_comment"


def test_get_default_business_impact_json_value():
    default_values = get_default_business_impact_json_value()

    # Check if the function returns a dictionary
    assert isinstance(default_values, dict)

    # Check if the dictionary has the expected keys from get_business_impact_fields
    expected_keys = [field[0] for field in get_business_impact_fields()]
    assert set(default_values.keys()) == set(expected_keys)

    # Check if the default values are as expected
    for key, value in default_values.items():
        assert value is False if isinstance(value, bool) else value == ""


def test_validate_business_impact_json():
    allowed_keys = get_default_business_impact_json_value().keys()

    # Test valid input
    valid_input = get_default_business_impact_json_value()
    validate_business_impact_json(valid_input)  # This should not raise any exception

    # Test invalid input - non-dictionary
    with pytest.raises(ValidationError, match="Invalid JSON. Must be a dictionary."):
        validate_business_impact_json("invalid_input")

    # Test invalid input - invalid key
    invalid_input_key = get_default_business_impact_json_value()
    invalid_input_key.update({"invalid_key": True})
    with pytest.raises(
        ValidationError,
        match=f"Invalid key: invalid_key. Only {','.join(allowed_keys)} are allowed.",
    ):
        validate_business_impact_json(invalid_input_key)

    # Test invalid input - invalid value type
    invalid_input_value = get_default_business_impact_json_value()
    invalid_input_value.update({"business_impact_high": "invalid_value"})
    with pytest.raises(
        ValidationError,
        match="Invalid value for key business_impact_high. Only boolean values are allowed.",
    ):
        validate_business_impact_json(invalid_input_value)

    # Test invalid input - missing keys
    invalid_input_missing_keys = {"business_impact_high": True}
    with pytest.raises(
        ValidationError,
        match="Data is missing the following fields: business_impact_medium,business_impact_low,business_impact_comment",
    ):
        validate_business_impact_json(invalid_input_missing_keys)


def test_convert_business_impact_fields_to_json():
    # Test valid input
    valid_input = get_default_business_impact_json_value()
    result = convert_business_impact_fields_to_json(valid_input)
    assert result == valid_input

    # Test invalid input - extra keys
    invalid_input_extra_keys = get_default_business_impact_json_value()
    invalid_input_extra_keys.update({"extra_key": True})
    result = convert_business_impact_fields_to_json(invalid_input_extra_keys)
    assert result == get_default_business_impact_json_value()
    assert "extra_key" not in result

    # Test invalid input - missing keys
    invalid_input_missing_keys = {}
    result = convert_business_impact_fields_to_json(invalid_input_missing_keys)
    assert result == {}
