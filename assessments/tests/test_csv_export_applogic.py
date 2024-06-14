from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock

import pandas as pd
import pytest
from freezegun import freeze_time
from pandas.testing import assert_frame_equal

from ..applogic import convert_to_dataframe, process_json_fields
from ..models import ComplianceCriticalityAssessment


@pytest.fixture
def sample_dataframe():
    data = {
        "id": [1, 2, 3],
        "gxp_impact": [{"a": 1}, {"b": 2}, {"c": 3}],
        "gxp_eres": [{"d": 4}, {"e": 5}, {"f": 6}],
        "sox_impact": [{"g": 7}, {"h": 8}, {"i": 9}],
        "privacy_impact": [{"j": 10}, {"k": 11}, {"l": 12}],
        "data_classification": [{"m": 13}, {"n": 14}, {"o": 15}],
        "business_impact": [{"p": 16}, {"q": 17}, {"r": 18}],
        "summary": [{"s": 16}, {"t": 17}, {"u": 18}],
        "rating": [{"v": 16}, {"w": 17}, {"x": 18}],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_queryset():
    queryset = MagicMock()
    queryset.values.return_value = [
        (1, {"a": 1}, {"d": 4}, {"g": 7}, {"j": 10}, {"m": 13}, {"p": 16}, "s1", 4.5),
        (2, {"b": 2}, {"e": 5}, {"h": 8}, {"k": 11}, {"n": 14}, {"q": 17}, "s2", 3.0),
        (3, {"c": 3}, {"f": 6}, {"i": 9}, {"l": 12}, {"o": 15}, {"r": 18}, "s3", 1.5),
    ]
    return queryset


def test_process_json_fields(sample_dataframe):
    result_df = process_json_fields(sample_dataframe)

    # Check if the columns are present in the result DataFrame
    expected_columns = [
        "id",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
    ]
    assert set(result_df.columns) == set(expected_columns)

    # Check if the values are correctly processed
    expected_data = {
        "id": [1, 2, 3],
        "a": [1, None, None],
        "b": [None, 2, None],
        "c": [None, None, 3],
        "d": [4, None, None],
        "e": [None, 5, None],
        "f": [None, None, 6],
        "g": [7, None, None],
        "h": [None, 8, None],
        "i": [None, None, 9],
        "j": [10, None, None],
        "k": [None, 11, None],
        "l": [None, None, 12],
        "m": [13, None, None],
        "n": [None, 14, None],
        "o": [None, None, 15],
        "p": [16, None, None],
        "q": [None, 17, None],
        "r": [None, None, 18],
        "s": [16, None, None],
        "t": [None, 17, None],
        "u": [None, None, 18],
        "v": [16, None, None],
        "w": [None, 17, None],
        "x": [None, None, 18],
    }

    expected_result_df = pd.DataFrame(expected_data)
    assert_frame_equal(result_df, expected_result_df, check_dtype=False)


@freeze_time("2012-01-14 12:00:00")
@pytest.mark.django_db
def test_convert_to_dataframe():
    queryset = ComplianceCriticalityAssessment.objects.all()
    df, filename = convert_to_dataframe(queryset)

    # Assertions
    assert isinstance(df, pd.DataFrame)
    assert isinstance(filename, str)

    assert filename == "Compliance_Criticality_Assessment_2012-01-14_12-00-00.csv"
