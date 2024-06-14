import pandas as pd
from django_pandas.io import read_frame
from pandas import json_normalize

from django.utils import dateformat, timezone


def process_json_fields(df: pd.DataFrame):
    json_fields_list = [
        "gxp_impact",
        "gxp_eres",
        "sox_impact",
        "privacy_impact",
        "data_classification",
        "business_impact",
        "summary",
        "rating",
    ]

    return pd.concat(
        [df.drop(json_fields_list, axis=1)]
        + [json_normalize(df[field]) for field in json_fields_list],
        axis=1,
    )


def convert_to_dataframe(queryset):

    current_time_string = dateformat.format(
        timezone.localtime(timezone.now()),
        "Y-m-d_H-i-s",
    )
    filename = f"Compliance_Criticality_Assessment_{current_time_string}.csv"
    df: pd.DataFrame = read_frame(queryset)
    df = process_json_fields(df)

    return df, filename
