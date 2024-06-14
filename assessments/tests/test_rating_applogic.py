import pytest

from django.core.exceptions import ValidationError

from ..applogic.rating_applogic import (
    calculate_rating,
    convert_rating_fields_to_json,
    get_default_rating_json_value,
    get_rating_fields,
    validate_rating_json,
)
from ..applogic.summary_applogic import get_default_summary_json_value


def test_get_rating_fields():
    fields = get_rating_fields()

    # Check if the function returns a list
    assert isinstance(fields, list)

    # Check if each element in the list is a tuple with two elements
    for field in fields:
        assert isinstance(field, tuple)
        assert len(field) == 2

    # The important thing to check here is the field names, the label can be anything as long as the field names don't change
    assert fields[0][0] == "rating_significant"
    assert fields[1][0] == "rating_moderate"
    assert fields[2][0] == "rating_minimal"
    assert fields[3][0] == "rating_no_compliance_risk"
    assert fields[4][0] == "rating_comment"


def test_get_default_rating_json_value():
    default_values = get_default_rating_json_value()

    # Check if the function returns a dictionary
    assert isinstance(default_values, dict)

    # Check if each field is assigned the correct default value
    for field, value in default_values.items():
        if field.endswith("_comment"):
            assert value == ""
        else:
            assert value is False

    # Check if the dictionary has the expected keys from get_rating_fields
    expected_keys = [field[0] for field in get_rating_fields()]
    assert set(default_values.keys()) == set(expected_keys)


def test_validate_rating_json():
    allowed_keys = get_default_rating_json_value().keys()

    # Test valid input
    valid_input = get_default_rating_json_value()
    validate_rating_json(valid_input)  # This should not raise any exception

    # Test invalid input - non-dictionary
    with pytest.raises(ValidationError, match="Invalid JSON. Must be a dictionary."):
        validate_rating_json("invalid_input")

    # Test invalid input - invalid key
    invalid_input_key = get_default_rating_json_value()
    invalid_input_key.update({"invalid_key": True})
    with pytest.raises(
        ValidationError,
        match=f"Invalid key: invalid_key. Only {','.join(allowed_keys)} are allowed.",
    ):
        validate_rating_json(invalid_input_key)

    # Test invalid input - invalid value type for boolean
    invalid_input_value = get_default_rating_json_value()
    invalid_input_value.update({"rating_significant": "invalid_value"})
    with pytest.raises(
        ValidationError,
        match="Invalid value for key rating_significant. Only boolean values are allowed.",
    ):
        validate_rating_json(invalid_input_value)

    # Test invalid input - missing keys
    invalid_input_missing_keys = get_default_rating_json_value()
    invalid_input_missing_keys.pop("rating_significant")
    with pytest.raises(
        ValidationError,
        match=f"Data is missing the following fields: rating_significant",
    ):
        validate_rating_json(invalid_input_missing_keys)


def test_convert_rating_fields_to_json():
    # Test valid input
    valid_input = get_default_rating_json_value()
    result = convert_rating_fields_to_json(valid_input)
    assert result == valid_input

    # Test invalid input - extra keys
    invalid_input_extra_keys = get_default_rating_json_value()
    invalid_input_extra_keys.update({"extra_key": True})
    result = convert_rating_fields_to_json(invalid_input_extra_keys)
    assert result == get_default_rating_json_value()
    assert "extra_key" not in result

    # Test invalid input - missing keys
    invalid_input_missing_keys = {}
    result = convert_rating_fields_to_json(invalid_input_missing_keys)
    assert result == {}


keys_to_test = get_default_summary_json_value().keys()


@pytest.mark.parametrize("key_to_set_true", keys_to_test)
def test_calculate_rating(key_to_set_true):
    summary_data = get_default_summary_json_value()
    summary_data[key_to_set_true] = True

    expected_rating = get_default_rating_json_value()

    grouping = {
        "significant_related_fields": [
            "summary_regulatory_gxp_impact_gmp",
            "summary_regulatory_gxp_impact_gcp",
            "summary_regulatory_gxp_impact_glp",
            "summary_regulatory_gxp_impact_gvp",
            "summary_data_classification_secret",
        ],
        "moderate_related_fields": [
            "summary_regulatory_gxp_impact_gxp_indirect",
            "summary_regulatory_sox_impact_sox",
            "summary_regulatory_privacy_impact_high_privacy",
            "summary_regulatory_privacy_impact_medium_privacy",
            "summary_data_classification_internal",
            "summary_data_classification_restricted",
            "summary_business_impact_high",
        ],
        "minimal_related_fields": [
            "summary_regulatory_gxp_impact_non_gxp",
            "summary_regulatory_privacy_impact_low_privacy",
            "summary_regulatory_sox_impact_non_sox",
            "summary_data_classification_public",
            "summary_business_impact_medium",
        ],
        "no_risk_related_fields": [
            "summary_regulatory_gxp_impact_non_gxp",
            "summary_regulatory_privacy_impact_no_privacy",
            "summary_regulatory_sox_impact_non_sox",
            "summary_business_impact_low",
        ],
    }

    if key_to_set_true in grouping["significant_related_fields"]:
        expected_rating["rating_significant"] = True
    elif key_to_set_true in grouping["moderate_related_fields"]:
        expected_rating["rating_moderate"] = True
    elif key_to_set_true in grouping["minimal_related_fields"]:
        expected_rating["rating_minimal"] = True
    else:
        expected_rating["rating_no_compliance_risk"] = True

    result = calculate_rating(summary_data)
    assert result == expected_rating
