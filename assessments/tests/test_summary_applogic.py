from unittest.mock import patch

import pytest

from django.core.exceptions import ValidationError

from ..applogic import (
    business_impact_applogic,
    data_classification_applogic,
    gxp_eres_applogic,
    gxp_impact_applogic,
    privacy_impact_applogic,
    sox_impact_applogic,
)
from ..applogic.summary_applogic import (
    calculate_summary,
    convert_summary_fields_to_json,
    get_audit_trail_summary,
    get_business_impact_summary,
    get_data_classification_summary,
    get_default_summary_json_value,
    get_gxp_eres_summary,
    get_gxp_impact_summary,
    get_privacy_impact_summary,
    get_sox_impact_summary,
    get_summary_fields,
    validate_summary_json,
)


def test_get_summary_fields():
    fields = get_summary_fields()

    # Check if the function returns a list
    assert isinstance(fields, list)

    # Check if each element in the list is a tuple with two elements
    for field in fields:
        assert isinstance(field, tuple)
        assert len(field) == 2

    # The important thing to check here is the field names, the label can be anything as long as the field names don't change
    assert fields[0][0] == "summary_regulatory_gxp_impact_gmp"
    assert fields[1][0] == "summary_regulatory_gxp_impact_gcp"
    assert fields[2][0] == "summary_regulatory_gxp_impact_glp"
    assert fields[3][0] == "summary_regulatory_gxp_impact_gvp"
    assert fields[4][0] == "summary_regulatory_gxp_impact_gxp_indirect"
    assert fields[5][0] == "summary_regulatory_gxp_impact_non_gxp"
    assert fields[6][0] == "summary_regulatory_sox_impact_sox"
    assert fields[7][0] == "summary_regulatory_sox_impact_non_sox"
    assert fields[8][0] == "summary_regulatory_gxp_eres_er"
    assert fields[9][0] == "summary_regulatory_gxp_eres_es"
    assert fields[10][0] == "summary_regulatory_gxp_eres_non_eres"
    assert fields[11][0] == "summary_regulatory_privacy_impact_high_privacy"
    assert fields[12][0] == "summary_regulatory_privacy_impact_medium_privacy"
    assert fields[13][0] == "summary_regulatory_privacy_impact_low_privacy"
    assert fields[14][0] == "summary_regulatory_privacy_impact_no_privacy"
    assert (
        fields[15][0] == "summary_regulatory_impact_administrative_audit_trail_review"
    )
    assert fields[16][0] == "summary_regulatory_impact_operational_audit_trail_review"
    assert fields[17][0] == "summary_data_classification_secret"
    assert fields[18][0] == "summary_data_classification_restricted"
    assert fields[19][0] == "summary_data_classification_internal"
    assert fields[20][0] == "summary_data_classification_public"
    assert fields[21][0] == "summary_business_impact_high"
    assert fields[22][0] == "summary_business_impact_medium"
    assert fields[23][0] == "summary_business_impact_low"


def test_get_summary_fields_grouped():
    fields = get_summary_fields(grouped=True)

    # Check if the function returns a list
    assert isinstance(fields, list)

    # Check if each element in the list is a tuple with two elements
    for group in fields:
        for field in group:
            assert isinstance(field, tuple)
            assert len(field) == 2

    # The important thing to check here is the field names, the label can be anything as long as the field names don't change
    assert fields[0][0][0] == "summary_regulatory_gxp_impact_gmp"
    assert fields[0][1][0] == "summary_regulatory_gxp_impact_gcp"
    assert fields[0][2][0] == "summary_regulatory_gxp_impact_glp"
    assert fields[0][3][0] == "summary_regulatory_gxp_impact_gvp"
    assert fields[0][4][0] == "summary_regulatory_gxp_impact_gxp_indirect"
    assert fields[0][5][0] == "summary_regulatory_gxp_impact_non_gxp"

    assert fields[1][0][0] == "summary_regulatory_sox_impact_sox"
    assert fields[1][1][0] == "summary_regulatory_sox_impact_non_sox"

    assert fields[2][0][0] == "summary_regulatory_gxp_eres_er"
    assert fields[2][1][0] == "summary_regulatory_gxp_eres_es"
    assert fields[2][2][0] == "summary_regulatory_gxp_eres_non_eres"

    assert fields[3][0][0] == "summary_regulatory_privacy_impact_high_privacy"
    assert fields[3][1][0] == "summary_regulatory_privacy_impact_medium_privacy"
    assert fields[3][2][0] == "summary_regulatory_privacy_impact_low_privacy"
    assert fields[3][3][0] == "summary_regulatory_privacy_impact_no_privacy"

    assert (
        fields[4][0][0] == "summary_regulatory_impact_administrative_audit_trail_review"
    )
    assert fields[4][1][0] == "summary_regulatory_impact_operational_audit_trail_review"

    assert fields[5][0][0] == "summary_data_classification_secret"
    assert fields[5][1][0] == "summary_data_classification_restricted"
    assert fields[5][2][0] == "summary_data_classification_internal"
    assert fields[5][3][0] == "summary_data_classification_public"

    assert fields[6][0][0] == "summary_business_impact_high"
    assert fields[6][1][0] == "summary_business_impact_medium"
    assert fields[6][2][0] == "summary_business_impact_low"


def test_get_default_summary_json_value():
    default_values = get_default_summary_json_value()

    # Check if the function returns a dictionary
    assert isinstance(default_values, dict)

    # Check if each field is assigned the correct default value
    for field, value in default_values.items():
        if field.endswith("_comment"):
            assert value == ""
        else:
            assert value is False

    # Check if the dictionary has the expected keys from get_summary_fields
    expected_keys = [field[0] for field in get_summary_fields()]
    assert set(default_values.keys()) == set(expected_keys)


def test_validate_summary_json():
    allowed_keys = get_default_summary_json_value().keys()

    # Test valid input
    valid_input = get_default_summary_json_value()
    validate_summary_json(valid_input)  # This should not raise any exception

    # Test invalid input - non-dictionary
    with pytest.raises(ValidationError, match="Invalid JSON. Must be a dictionary."):
        validate_summary_json("invalid_input")

    # Test invalid input - invalid key
    invalid_input_key = get_default_summary_json_value()
    invalid_input_key.update({"invalid_key": True})
    with pytest.raises(
        ValidationError,
        match=f"Invalid key: invalid_key. Only {','.join(allowed_keys)} are allowed.",
    ):
        validate_summary_json(invalid_input_key)

    # Test invalid input - invalid value type for boolean
    invalid_input_value = get_default_summary_json_value()
    invalid_input_value.update({"summary_regulatory_gxp_impact_gmp": "invalid_value"})
    with pytest.raises(
        ValidationError,
        match="Invalid value for key summary_regulatory_gxp_impact_gmp. Only boolean values are allowed.",
    ):
        validate_summary_json(invalid_input_value)

    # Test invalid input - missing keys
    invalid_input_missing_keys = get_default_summary_json_value()
    invalid_input_missing_keys.pop("summary_regulatory_gxp_impact_gmp")
    with pytest.raises(
        ValidationError,
        match=f"Data is missing the following fields: summary_regulatory_gxp_impact_gmp",
    ):
        validate_summary_json(invalid_input_missing_keys)


def test_convert_summary_fields_to_json():
    # Test valid input
    valid_input = get_default_summary_json_value()
    result = convert_summary_fields_to_json(valid_input)
    assert result == valid_input

    # Test invalid input - extra keys
    invalid_input_extra_keys = get_default_summary_json_value()
    invalid_input_extra_keys.update({"extra_key": True})
    result = convert_summary_fields_to_json(invalid_input_extra_keys)
    assert result == get_default_summary_json_value()
    assert "extra_key" not in result

    # Test invalid input - missing keys
    invalid_input_missing_keys = {}
    result = convert_summary_fields_to_json(invalid_input_missing_keys)
    assert result == {}


def test_calculate_summary_calls_all_get_functions():
    cca_data = {
        "gxp_impact": "some_value",
        "sox_impact": "some_value",
        "gxp_eres": "some_value",
        "privacy_impact": "some_value",
        "data_classification": "some_value",
        "business_impact": "some_value",
    }

    with patch(
        "assessments.applogic.summary_applogic.get_default_summary_json_value"
    ) as mock_default_summary, patch(
        "assessments.applogic.summary_applogic.get_gxp_impact_summary"
    ) as mock_gxp_impact, patch(
        "assessments.applogic.summary_applogic.get_sox_impact_summary"
    ) as mock_sox_impact, patch(
        "assessments.applogic.summary_applogic.get_gxp_eres_summary"
    ) as mock_gxp_eres, patch(
        "assessments.applogic.summary_applogic.get_privacy_impact_summary"
    ) as mock_privacy_impact, patch(
        "assessments.applogic.summary_applogic.get_data_classification_summary"
    ) as mock_data_classification, patch(
        "assessments.applogic.summary_applogic.get_business_impact_summary"
    ) as mock_business_impact, patch(
        "assessments.applogic.summary_applogic.get_audit_trail_summary"
    ) as mock_audit_trail:

        summary = calculate_summary(cca_data)

        mock_default_summary.assert_called_once()
        mock_gxp_impact.assert_called_once_with(
            mock_default_summary.return_value, cca_data["gxp_impact"]
        )
        mock_sox_impact.assert_called_once_with(
            mock_gxp_impact.return_value, cca_data["sox_impact"]
        )
        mock_gxp_eres.assert_called_once_with(
            mock_sox_impact.return_value, cca_data["gxp_eres"]
        )
        mock_privacy_impact.assert_called_once_with(
            mock_gxp_eres.return_value, cca_data["privacy_impact"]
        )
        mock_data_classification.assert_called_once_with(
            mock_privacy_impact.return_value, cca_data["data_classification"]
        )
        mock_business_impact.assert_called_once_with(
            mock_data_classification.return_value, cca_data["business_impact"]
        )
        mock_audit_trail.assert_called_once_with(mock_business_impact.return_value)


keys_to_test = [
    field[0]
    for field in gxp_impact_applogic.get_gxp_impact_fields(without_comments=True)
]


@pytest.mark.parametrize("key_to_set_true", keys_to_test)
def test_get_gxp_impact_summary(key_to_set_true):
    summary = get_default_summary_json_value()
    data_set = gxp_impact_applogic.get_default_gxp_impact_json_value()

    # check while all fields are false
    result = get_gxp_impact_summary(summary, data_set)
    summary["summary_regulatory_gxp_impact_non_gxp"] = True
    assert result == summary

    # check when one of the fields is true
    data_set[key_to_set_true] = True
    summary["summary_regulatory_gxp_impact_non_gxp"] = False
    result = get_gxp_impact_summary(summary, data_set)
    if key_to_set_true in gxp_impact_applogic.get_gmp_related_fields():
        summary["summary_regulatory_gxp_impact_gmp"] = True
    elif key_to_set_true in gxp_impact_applogic.get_gcp_related_fields():
        summary["summary_regulatory_gxp_impact_gcp"] = True
    elif key_to_set_true in gxp_impact_applogic.get_glp_related_fields():
        summary["summary_regulatory_gxp_impact_glp"] = True
    elif key_to_set_true in gxp_impact_applogic.get_gvp_related_fields():
        summary["summary_regulatory_gxp_impact_gvp"] = True
    elif key_to_set_true in gxp_impact_applogic.get_gxp_indirect_related_fields():
        summary["summary_regulatory_gxp_impact_gxp_indirect"] = True

    assert result == summary


keys_to_test = [
    field[0]
    for field in sox_impact_applogic.get_sox_impact_fields(without_comments=True)
]


@pytest.mark.parametrize("key_to_set_true", keys_to_test)
def test_get_sox_impact_summary(key_to_set_true):
    summary = get_default_summary_json_value()
    data_set = sox_impact_applogic.get_default_sox_impact_json_value()

    # check while all fields are false
    result = get_sox_impact_summary(summary, data_set)
    summary["summary_regulatory_sox_impact_non_sox"] = True
    assert result == summary

    # check when one of the fields is true
    data_set[key_to_set_true] = True
    summary["summary_regulatory_sox_impact_sox"] = True
    result = get_sox_impact_summary(summary, data_set)

    assert result == summary


keys_to_test = [
    field[0] for field in gxp_eres_applogic.get_gxp_eres_fields(without_comments=True)
]


@pytest.mark.parametrize("key_to_set_true", keys_to_test)
def test_get_gxp_eres_summary(key_to_set_true):
    summary = get_default_summary_json_value()
    data_set = gxp_eres_applogic.get_default_gxp_eres_json_value()

    # check while all fields are false
    result = get_gxp_eres_summary(summary, data_set)
    summary["summary_regulatory_gxp_eres_non_eres"] = True
    assert result == summary

    # check when one of the fields is true
    data_set[key_to_set_true] = True
    summary["summary_regulatory_gxp_eres_non_gxp"] = False
    result = get_gxp_eres_summary(summary, data_set)
    if key_to_set_true in gxp_eres_applogic.get_gxp_er_related_fields():
        summary["summary_regulatory_gxp_eres_er"] = True
    elif key_to_set_true in gxp_eres_applogic.get_gxp_es_related_fields():
        summary["summary_regulatory_gxp_eres_es"] = True

    assert result == summary


def test_get_privacy_impact_summary():
    data_set = privacy_impact_applogic.get_default_privacy_impact_json_value()
    fields = list(data_set.keys())

    # both false
    data_set[fields[0]] = False
    data_set[fields[1]] = False
    summary = get_default_summary_json_value()
    result = get_privacy_impact_summary(summary, data_set)
    summary["summary_regulatory_privacy_impact_no_privacy"] = True
    assert result == summary

    # q1 is false q2 is true
    data_set[fields[0]] = False
    data_set[fields[1]] = True
    summary = get_default_summary_json_value()
    result = get_privacy_impact_summary(summary, data_set)
    summary["summary_regulatory_privacy_impact_low_privacy"] = True
    assert result == summary

    # q1 is true q2 is false
    data_set[fields[0]] = True
    data_set[fields[1]] = False
    summary = get_default_summary_json_value()
    result = get_privacy_impact_summary(summary, data_set)
    summary["summary_regulatory_privacy_impact_medium_privacy"] = True
    assert result == summary

    # both true
    data_set[fields[0]] = True
    data_set[fields[1]] = False
    summary = get_default_summary_json_value()
    result = get_privacy_impact_summary(summary, data_set)
    summary["summary_regulatory_privacy_impact_high_privacy"] = True
    assert result == summary


keys_to_test = [
    field[0] for field in data_classification_applogic.get_data_classification_fields()
]


@pytest.mark.parametrize("key_to_set_true", keys_to_test)
def test_get_data_classification_summary(key_to_set_true):
    summary = get_default_summary_json_value()
    data_set = data_classification_applogic.get_default_data_classification_json_value()
    data_set[key_to_set_true] = True

    # data classification is one to one to summary
    summary[f"summary_{key_to_set_true}"] = True
    result = get_data_classification_summary(summary, data_set)

    assert result == summary


keys_to_test = [
    field[0] for field in business_impact_applogic.get_business_impact_fields()
]


@pytest.mark.parametrize("key_to_set_true", keys_to_test)
def test_get_business_impact_summary(key_to_set_true):
    summary = get_default_summary_json_value()
    data_set = business_impact_applogic.get_default_business_impact_json_value()
    data_set[key_to_set_true] = True

    # business impact is one to one to summary
    summary[f"summary_{key_to_set_true}"] = True
    result = get_business_impact_summary(summary, data_set)

    assert result == summary


operational_related_fields = [
    "summary_regulatory_gxp_impact_gmp",
    "summary_regulatory_gxp_impact_gcp",
    "summary_regulatory_gxp_impact_glp",
    "summary_regulatory_gxp_impact_gvp",
]


@pytest.mark.parametrize("key_to_set_true", operational_related_fields)
def test_get_operational_audit_trail_summary(key_to_set_true):
    summary = get_default_summary_json_value()

    # check while all fields are false
    result = get_audit_trail_summary(summary)
    assert result == summary

    # any of the fields should set this to true
    summary[key_to_set_true] = True
    summary["summary_regulatory_impact_operational_audit_trail_review"] = True
    result = get_audit_trail_summary(summary)

    assert result == summary


admin_related_fields = operational_related_fields + [
    "summary_regulatory_gxp_impact_gxp_indirect"
]


@pytest.mark.parametrize("key_to_set_true", admin_related_fields)
def test_get_admin_audit_trail_summary(key_to_set_true):
    summary = get_default_summary_json_value()

    # check while all fields are false
    result = get_audit_trail_summary(summary)
    assert result == summary

    # any of the fields should set this to true
    summary[key_to_set_true] = True
    summary["summary_regulatory_impact_admin_audit_trail_review"] = True
    result = get_audit_trail_summary(summary)

    assert result == summary
