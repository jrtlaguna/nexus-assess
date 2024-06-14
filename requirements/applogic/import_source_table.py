import math
from itertools import chain

import numpy as np
import pandas as pd

from django.db import transaction

from requirements.models import (
    Compliance,
    ComplianceCategory,
    Reference,
    ReferenceCategory,
    ReferencePolicy,
    Requirement,
    RequirementCategory,
)

NULL_SET = [math.nan, None, "", "nan", np.nan]


def format_header(string: str) -> str:
    return string.strip().replace(" ", "_").replace("/", "_").lower()


def breakdown_references(string: str) -> str:
    group = string.split("\n")
    return list(map(str.strip, group))


def import_source_table(df: pd.DataFrame) -> pd.DataFrame:
    # cleanup unnecessary spaces to column names
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    header_df = df[:2]
    # clean and set new headers
    new_header = list(map(format_header, df.iloc[1]))
    df = df[2:]  # take the data less the header row
    df.columns = new_header  # set the header row as the df header

    # compliance
    compliance_headers = header_df.iloc[:, 9:27].T

    compliance_set = []

    with transaction.atomic():
        for category, compliance in compliance_headers.itertuples(index=False):
            if isinstance(category, str):
                # get or create using slug
                current_category, _ = ComplianceCategory.objects.get_or_create(
                    name=category.strip()
                )
            compliance_set.append(
                Compliance(
                    category=current_category,
                    name=compliance,
                    header_name=format_header(compliance),
                )
            )
        Compliance.objects.bulk_create(compliance_set)
        compliance_headers = Compliance.objects.values_list("header_name", flat=True)

        # references
        references_headers = header_df.iloc[:, 28:48].T

        reference_policy_set = []
        for category, reference_policy in list(
            references_headers.itertuples(index=False)
        ):
            if isinstance(category, str):
                current_category, _ = ReferenceCategory.objects.get_or_create(
                    name=category
                )
            reference_policy_set.append(
                ReferencePolicy(
                    name=reference_policy,
                    category=current_category,
                    header_name=format_header(reference_policy),
                )
            )

        reference_policies = ReferencePolicy.objects.bulk_create(reference_policy_set)

        references_set = []
        for policy in reference_policies:
            reference_set = [
                breakdown_references(string)
                for string in df[policy.header_name].dropna().unique().astype(str)
            ]

            # flatten
            flat_list = list(
                set(item.strip() for sublist in reference_set for item in sublist)
            )
            if "" in flat_list:
                flat_list.remove("")

            references_set += [
                Reference(identifier=identifier, policy=policy)
                for identifier in flat_list
            ]

        Reference.objects.bulk_create(references_set)

        requirement_categories_set = [
            RequirementCategory(name=category)
            for category in df["category"].unique().astype(str)
        ]
        requirement_categories = RequirementCategory.objects.bulk_create(
            requirement_categories_set
        )
        requirement_categories_dict = {
            category.name: category for category in requirement_categories
        }

        policy_list = ReferencePolicy.objects.values_list("header_name", flat=True)

        for _, row in df.iterrows():
            requirement, _ = Requirement.objects.get_or_create(
                control_id=row["control_requirement_id"],
                category=requirement_categories_dict[row["category"]],
            )

            requirement.organization = row["organization"] == "x"
            requirement.analytical_instruments = row["analytical_instruments"] == "x"
            requirement.saas_application = row["saas_application"] == "x"
            requirement.paas = row["paas"] == "x"
            requirement.iaas_infrastructure = row["iaas_infrastructure"] == "x"
            requirement.baseline = row["baseline"] == "x"
            requirement.control_statement = row["control_statement"]
            requirement.requirement_statement = row["requirement_statement"]
            requirement.bbb_common_solution = (
                row["bbb_common_solution"].strip()
                if row["bbb_common_solution"] not in NULL_SET
                else ""
            )
            requirement.test_guidance = row["test_guidance"]

            not_null_columns = row[row.notna()].index.tolist()

            matched_columns = list(set(policy_list) & set(not_null_columns))

            requirement_references = [
                reference.split("\n")
                for reference in row[matched_columns].unique().astype(str)
            ]
            cleaned_reference = list(set(chain(*requirement_references)))
            if "" in cleaned_reference:
                cleaned_reference.remove("")

            requirement.references.set(
                Reference.objects.filter(identifier__in=cleaned_reference)
            )

            matched_compliances = list(set(not_null_columns) & set(compliance_headers))

            requirement.compliances.set(
                Compliance.objects.filter(header_name__in=matched_compliances)
            )
            requirement.save()

    return df
