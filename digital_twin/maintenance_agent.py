
import math
from typing import List, Optional


ACTION_CATALOG = {
    "Battery Health Diagnostics": {
        "action_steps": [
            "Verify the SOH estimate using appropriate diagnostic measurements.",
            "Review available battery fault codes and degradation history.",
            "Follow the manufacturer's battery inspection procedure.",
        ],
        "required_evidence": [
            "Current SOH estimate",
            "Recent SOH observations",
        ],
    },
    "Thermal Management Inspection": {
        "action_steps": [
            "Review battery temperature history and thermal fault codes.",
            "Check cooling-system operation using the approved service procedure.",
            "Escalate abnormal temperatures to a qualified technician.",
        ],
        "required_evidence": [
            "Battery temperature readings or thermal fault codes",
        ],
    },
    "Battery Management System Check": {
        "action_steps": [
            "Read available battery-management-system fault codes.",
            "Review sensor readings and cell-voltage differences if available.",
            "Refer confirmed abnormalities to a qualified technician.",
        ],
        "required_evidence": [
            "BMS fault codes or cell-level diagnostic data",
        ],
    },
    "Charging and Usage Review": {
        "action_steps": [
            "Review available charging history and operating conditions.",
            "Check temperature and charging events for abnormal patterns.",
            "Compare observed operation with manufacturer guidance.",
        ],
        "required_evidence": [
            "Charging history or operating-condition records",
        ],
    },
    "Qualified Repair/Replacement Assessment": {
        "action_steps": [
            "Arrange a qualified battery-system assessment.",
            "Verify degradation and investigate confirmed faults.",
            "Consider repair or replacement only under manufacturer criteria.",
        ],
        "required_evidence": [
            "Diagnostic confirmation and applicable service criteria",
        ],
    },
}


def recommend_maintenance(
    scenario_results: List[dict],
    minimum_acceptable_soh: float = 0.80,
    current_soh: Optional[float] = None,
    trend_per_sample: Optional[float] = None,
    diagnostic_evidence: Optional[dict] = None,
) -> dict:
    """Select an adaptive action using condition and scenario outcomes.

    Maintenance effects remain illustrative. This policy does not
    diagnose physical faults from SOH or trend data alone.
    """
    if not scenario_results:
        raise ValueError("At least one scenario result is required.")

    def valid_fraction(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            and 0.0 <= value <= 1.0
        )

    if not valid_fraction(minimum_acceptable_soh):
        raise ValueError(
            "Minimum acceptable SOH must be finite and between 0 and 1."
        )

    if current_soh is not None and not valid_fraction(current_soh):
        raise ValueError("Current SOH must be finite and between 0 and 1.")

    if trend_per_sample is not None and (
        isinstance(trend_per_sample, bool)
        or not isinstance(trend_per_sample, (int, float))
        or not math.isfinite(trend_per_sample)
    ):
        raise ValueError("Trend must be a finite number.")
    
    if diagnostic_evidence is None:
        diagnostic_evidence = {}

    if not isinstance(diagnostic_evidence, dict):
        raise ValueError("Diagnostic evidence must be a dictionary.")

    allowed_evidence = {
        "thermal_alert",
        "bms_fault_codes",
        "cell_voltage_imbalance",
        "charging_anomaly",
        "confirmed_fault",
    }

    unknown_evidence = set(diagnostic_evidence) - allowed_evidence
    if unknown_evidence:
        raise ValueError(
            f"Unsupported diagnostic evidence fields: {sorted(unknown_evidence)}"
        )

    for key in (
        "thermal_alert",
        "cell_voltage_imbalance",
        "charging_anomaly",
        "confirmed_fault",
    ):
        if key in diagnostic_evidence and not isinstance(
            diagnostic_evidence[key], bool
        ):
            raise ValueError(f"{key} must be a boolean.")

    if "bms_fault_codes" in diagnostic_evidence:
        codes = diagnostic_evidence["bms_fault_codes"]
        if (
            not isinstance(codes, list)
            or any(not isinstance(code, str) or not code.strip() for code in codes)
        ):
            raise ValueError("bms_fault_codes must be a list of non-empty strings.")

    validated = []
    for result in scenario_results:
        if not isinstance(result, dict):
            raise ValueError("Each scenario result must be a dictionary.")

        if "scenario" not in result or "projected_soh" not in result:
            raise ValueError(
                "Each result must include scenario and projected_soh."
            )

        if not isinstance(result["scenario"], str) or not result["scenario"].strip():
            raise ValueError("Scenario names must be non-empty strings.")

        if not valid_fraction(result["projected_soh"]):
            raise ValueError(
                "Projected SOH must be finite and between 0 and 1."
            )

        validated.append(result)

    baseline = next(
        (r for r in validated if r["scenario"] == "No maintenance"),
        None,
    )

    best = max(validated, key=lambda r: r["projected_soh"])
    acceptable = [
        r for r in validated
        if r["projected_soh"] >= minimum_acceptable_soh
    ]

    declining = (
        trend_per_sample is not None and trend_per_sample < 0
    )
    rapid_decline = (
        trend_per_sample is not None and trend_per_sample <= -0.001
    )
    low_soh = (
        current_soh is not None
        and current_soh < minimum_acceptable_soh
    )
    baseline_acceptable = (
        baseline is not None
        and baseline["projected_soh"] >= minimum_acceptable_soh
    )

    # Select a scenario first; this is not a physical fault diagnosis.
    if not acceptable:
        selected = best
        status = "below_threshold"
    elif (low_soh or rapid_decline) and any(
        r["scenario"] != "No maintenance" for r in acceptable
    ):
        selected = max(
            (r for r in acceptable if r["scenario"] != "No maintenance"),
            key=lambda r: r["projected_soh"],
        )
        status = "maintenance_preferred_by_condition"
    elif baseline_acceptable:
        selected = baseline
        status = "acceptable_under_assumptions"
    else:
        selected = max(
            acceptable, key=lambda r: r["projected_soh"]
        )
        status = "acceptable_under_assumptions"

    # Choose a supported general action from available evidence.

    evidence = diagnostic_evidence

    thermal_alert = evidence.get("thermal_alert", False)
    bms_fault_codes = evidence.get("bms_fault_codes", [])
    cell_imbalance = evidence.get("cell_voltage_imbalance", False)
    charging_anomaly = evidence.get("charging_anomaly", False)
    confirmed_fault = evidence.get("confirmed_fault", False)

    # Prioritize evidence-supported actions over generic SOH-based advice.
    if confirmed_fault:
        action = "Qualified Repair/Replacement Assessment"
        urgency = "high"
        reason = (
            "A fault has been reported as confirmed. Arrange a qualified "
            "assessment and follow the manufacturer's service criteria."
        )
    elif thermal_alert:
        action = "Thermal Management Inspection"
        urgency = "high"
        reason = (
            "Thermal alert evidence was supplied. Review temperature data "
            "and arrange inspection using the approved service procedure."
        )
    elif bms_fault_codes or cell_imbalance:
        action = "Battery Management System Check"
        urgency = "high" if bms_fault_codes else "moderate"
        reason = (
            "BMS fault-code or cell-voltage imbalance evidence was supplied. "
            "Review diagnostic records and escalate confirmed abnormalities."
        )
    elif charging_anomaly:
        action = "Charging and Usage Review"
        urgency = "moderate"
        reason = (
            "Charging anomaly evidence was supplied. Review charging history "
            "and compare operating conditions with manufacturer guidance."
        )
    elif status == "below_threshold" or low_soh or rapid_decline:
        action = "Battery Health Diagnostics"
        urgency = "high" if low_soh or status == "below_threshold" else "moderate"
        reason = (
            "Battery condition or projected SOH warrants diagnostic "
            "assessment. SOH data alone does not establish a physical fault."
        )
    elif declining:
        action = "Battery Health Diagnostics"
        urgency = "moderate"
        reason = (
            "The observed SOH trend is declining. Verify the estimate and "
            "investigate the cause before selecting a physical repair."
        )
    else:
        action = "Charging and Usage Review"
        urgency = "routine"
        reason = (
            "No diagnostic fault evidence was supplied. Review operating "
            "history if available and continue condition monitoring."
        )

    details = ACTION_CATALOG[action]

    if status == "below_threshold":
        reason += (
            " No simulated scenario meets the configured SOH threshold; "
            "professional assessment is needed."
        )

    return {
        "recommended_scenario": selected["scenario"],
        "projected_soh": selected["projected_soh"],
        "status": status,
        "reason": reason,
        "current_soh": current_soh,
        "trend_per_sample": trend_per_sample,
        "minimum_acceptable_soh": minimum_acceptable_soh,
        "recommended_action": action,
        "action_steps": details["action_steps"],
        "required_evidence": details["required_evidence"],
        "urgency": urgency,
        "decision_factors": {
            "current_soh_below_threshold": low_soh,
            "trend_is_declining": declining,
            "trend_indicates_rapid_decline": rapid_decline,
            "baseline_meets_threshold": baseline_acceptable,
            "acceptable_scenario_count": len(acceptable),
        },
        "available_action_categories": list(ACTION_CATALOG.keys()),
        "is_adaptive_policy": True,
        "is_simulation_based": True,
        "is_rule_based": True,
        "maintenance_effects_validated": False,
    }
