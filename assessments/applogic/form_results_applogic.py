from django.db.models import Q

from requirements.models import Compliance, Requirement


def get_form_results(form):
    selected_compliances = []

    form_summary = form.summary
    form_rating = form.rating

    # Mapping of summary keys to compliance header names
    summary_mapping = {
        "summary_regulatory_gxp_impact_non_gxp": ("non-gxp",),
        "summary_regulatory_gxp_impact_glp": ("glp__gcp",),
        "summary_regulatory_gxp_impact_gcp": ("glp__gcp",),
        "summary_regulatory_gxp_impact_gvp": ("gpvp",),
        "summary_regulatory_sox_impact_sox": ("sox",),
        "summary_regulatory_gxp_impact_gxp_indirect": ("gmp-indirect", "gmp-direct"),
        "summary_regulatory_gxp_eres_non_eres": ("no_impact", "impact"),
    }

    # Mapping of summary keys to compliance header names
    for key, value in summary_mapping.items():
        if form_summary.get(key):
            selected_compliances.append(value[0])
        else:
            if len(value) > 1:
                selected_compliances.append(value[1])

    # Mapping of rating keys to compliance header names
    rating_mapping = {
        "rating_significant": "significant",
        "rating_moderate": "moderate",
        "rating_minimal": "minimal",
    }

    rating = None
    for key, value in rating_mapping.items():
        if form_rating.get(key):
            rating = Compliance.objects.get(header_name=value)
            break

    # Mapping of privacy keys to compliance header names
    privacy_mapping = {
        "summary_regulatory_privacy_impact_high_privacy": "high_privacy",
        "summary_regulatory_privacy_impact_medium_privacy": "medium_privacy",
        "summary_regulatory_privacy_impact_low_privacy": "low_privacy",
    }

    for key, value in privacy_mapping.items():
        if form_summary.get(key):
            selected_compliances.append(value)
            break

    # Determine solution type
    hosting_types = {
        "on_premises": Q(analytical_instruments=True),
        "third_party": Q(saas_application=True),
        "website": Q(saas_application=True),
        "saas": Q(saas_application=True),
        "paas": Q(paas=True),
        "iaas": Q(iaas_infrastructure=True),
    }
    solution_type_query = hosting_types.get(form.hosting_and_type)

    filtered_by_applicability = Requirement.objects.filter(solution_type_query)
    filtered_by_baseline_and_criticality = filtered_by_applicability.filter(
        Q(baseline=True) & Q(compliances=rating)
    )
    compliances = Compliance.objects.filter(header_name__in=selected_compliances)
    filtered_by_compliance = filtered_by_applicability.filter(
        Q(compliances__in=compliances)
    )
    requirements = (
        (filtered_by_baseline_and_criticality | filtered_by_compliance)
        .distinct()
        .order_by("control_id")
    )

    return requirements
