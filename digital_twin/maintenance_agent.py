
from typing import List, Optional


def recommend_maintenance(
    scenario_results: List[dict],
    minimum_acceptable_soh: float = 0.80,
    current_soh: Optional[float] = None,
    trend_per_sample: Optional[float] = None,
) -> dict:
    """
    Recommend a maintenance scenario using explicit condition-aware rules.

    Scenario outcomes and maintenance effects are illustrative simulations.
    The trend is expressed as SOH fraction change per observation.
    """
    if not scenario_results:
        raise ValueError("At least one scenario result is required.")

    if not 0.0 <= minimum_acceptable_soh <= 1.0:
        raise ValueError(
            "Minimum acceptable SOH must be between 0 and 1."
        )

    if current_soh is not None and not 0.0 <= current_soh <= 1.0:
        raise ValueError("Current SOH must be between 0 and 1.")

    if trend_per_sample is not None:
        if trend_per_sample != trend_per_sample:
            raise ValueError("Trend must be a finite number.")
        if abs(trend_per_sample) == float("inf"):
            raise ValueError("Trend must be a finite number.")

    for result in scenario_results:
        if "scenario" not in result or "projected_soh" not in result:
            raise ValueError(
                "Each result must include scenario and projected_soh."
            )

        if not 0.0 <= result["projected_soh"] <= 1.0:
            raise ValueError("Projected SOH must be between 0 and 1.")

    acceptable_scenarios = [
        result
        for result in scenario_results
        if result["projected_soh"] >= minimum_acceptable_soh
    ]

    baseline: Optional[dict] = next(
        (
            result
            for result in scenario_results
            if result["scenario"] == "No maintenance"
        ),
        None,
    )

    # If no scenario meets the threshold, report the best available
    # outcome while clearly indicating that further assessment is needed.
    if not acceptable_scenarios:
        recommended = max(
            scenario_results,
            key=lambda result: result["projected_soh"],
        )
        status = "below_threshold"
        reason = (
            "No scenario meets the minimum acceptable SOH. "
            "The highest projected SOH scenario is reported, but "
            "further assessment is needed."
        )

    # If the current battery is already below the threshold, or the
    # recent trend is strongly negative, prefer the best acceptable
    # maintenance scenario when one is available.
    elif (
        current_soh is not None
        and current_soh < minimum_acceptable_soh
    ) or (
        trend_per_sample is not None
        and trend_per_sample <= -0.001
    ):
        maintenance_options = [
            result
            for result in acceptable_scenarios
            if result["scenario"] != "No maintenance"
        ]

        if maintenance_options:
            recommended = max(
                maintenance_options,
                key=lambda result: result["projected_soh"],
            )
            status = "maintenance_preferred_by_condition"
            reason = (
                "Current battery condition or recent degradation trend "
                "indicates increased concern. The best acceptable "
                "maintenance scenario is preferred under the configured "
                "simulation assumptions."
            )
        elif baseline in acceptable_scenarios:
            recommended = baseline
            status = "acceptable_under_assumptions"
            reason = (
                "The baseline meets the SOH threshold, and no acceptable "
                "maintenance alternative is available."
            )
        else:
            recommended = max(
                acceptable_scenarios,
                key=lambda result: result["projected_soh"],
            )
            status = "acceptable_under_assumptions"
            reason = "Selected the acceptable scenario with the highest projected SOH."

    # Under stable conditions, retain the no-maintenance baseline if
    # it meets the threshold; otherwise select the best acceptable result.
    elif baseline in acceptable_scenarios:
        recommended = baseline
        status = "acceptable_under_assumptions"
        reason = (
            "The baseline meets the configured SOH threshold, and the "
            "condition-aware rules do not indicate increased concern."
        )
    else:
        recommended = max(
            acceptable_scenarios,
            key=lambda result: result["projected_soh"],
        )
        status = "acceptable_under_assumptions"
        reason = (
            "The baseline does not meet the threshold. Selected the "
            "acceptable scenario with the highest projected SOH."
        )

    return {
        "recommended_scenario": recommended["scenario"],
        "projected_soh": recommended["projected_soh"],
        "status": status,
        "reason": reason,
        "current_soh": current_soh,
        "trend_per_sample": trend_per_sample,
        "minimum_acceptable_soh": minimum_acceptable_soh,
        "is_simulation_based": True,
        "is_rule_based": True,
    }
