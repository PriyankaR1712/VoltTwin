
from typing import List, Optional


def recommend_maintenance(
    scenario_results: List[dict],
    minimum_acceptable_soh: float = 0.80,
) -> dict:
    """
    Recommend a scenario using projected SOH and explicit constraints.

    All scenario outcomes are simulations. This simple rule-based
    agent does not establish real-world maintenance effectiveness.
    """
    if not scenario_results:
        raise ValueError("At least one scenario result is required.")

    if not 0.0 <= minimum_acceptable_soh <= 1.0:
        raise ValueError(
            "Minimum acceptable SOH must be between 0 and 1."
        )

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

    if not acceptable_scenarios:
        best = max(
            scenario_results,
            key=lambda result: result["projected_soh"],
        )

        return {
            "recommended_scenario": best["scenario"],
            "projected_soh": best["projected_soh"],
            "status": "below_threshold",
            "reason": (
                "No scenario meets the minimum acceptable SOH. "
                "The highest projected SOH scenario is reported, "
                "but further assessment is needed."
            ),
            "is_simulation_based": True,
        }

    baseline: Optional[dict] = next(
        (
            result
            for result in scenario_results
            if result["scenario"] == "No maintenance"
        ),
        None,
    )

    # Prefer no maintenance when it meets the threshold.
    # Otherwise choose the acceptable scenario with the highest
    # projected SOH. This is a simple baseline policy, not a
    # cost-optimized or safety-validated maintenance policy.
    if baseline is not None and baseline in acceptable_scenarios:
        recommended = baseline
    else:
        recommended = max(
            acceptable_scenarios,
            key=lambda result: result["projected_soh"],
        )

    return {
        "recommended_scenario": recommended["scenario"],
        "projected_soh": recommended["projected_soh"],
        "status": "acceptable_under_assumptions",
        "reason": (
            f"The selected scenario meets the configured SOH "
            f"threshold of {minimum_acceptable_soh:.0%}. "
            "The recommendation is based on simulated outcomes "
            "and the current rule-based policy."
        ),
        "is_simulation_based": True,
    }
