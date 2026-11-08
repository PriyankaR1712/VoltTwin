"""Validated goal contract for the experimental planner."""

import math
from dataclasses import dataclass
from typing import Optional


ASSESSMENT_SCOPES = frozenset(
    {"baseline_only", "counterfactual_comparison", "auto"}
)
SUPPORTED_DIAGNOSTIC_EVIDENCE = frozenset(
    {
        "thermal_alert",
        "bms_fault_codes",
        "cell_voltage_imbalance",
        "charging_anomaly",
        "confirmed_fault",
    }
)
_BOOLEAN_EVIDENCE = frozenset(
    {
        "thermal_alert",
        "cell_voltage_imbalance",
        "charging_anomaly",
        "confirmed_fault",
    }
)


def _validate_optional_soh(value: object, field: str) -> None:
    if value is None:
        return
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0.0 <= value <= 1.0
    ):
        raise ValueError(f"{field} must be finite and between 0 and 1.")


def validate_diagnostic_evidence(evidence: Optional[dict]) -> None:
    if evidence is None:
        return
    if not isinstance(evidence, dict):
        raise ValueError("Diagnostic evidence must be a dictionary.")
    unknown = set(evidence) - SUPPORTED_DIAGNOSTIC_EVIDENCE
    if unknown:
        raise ValueError(f"Unsupported diagnostic evidence fields: {sorted(unknown)}")
    for key in _BOOLEAN_EVIDENCE:
        if key in evidence and not isinstance(evidence[key], bool):
            raise ValueError(f"{key} must be a boolean.")
    if "bms_fault_codes" in evidence:
        codes = evidence["bms_fault_codes"]
        if not isinstance(codes, list) or any(
            not isinstance(code, str) or not code.strip() for code in codes
        ):
            raise ValueError("bms_fault_codes must be a list of non-empty strings.")


@dataclass(frozen=True)
class GoalSpec:
    """A deterministic, versioned goal and its requested evaluation horizon."""

    goal_id: str
    horizon_cycles: int
    target_soh: Optional[float] = None
    assessment_scope: str = "auto"
    diagnostic_evidence: Optional[dict] = None
    goal_version: str = "goal_v1"
    config_version: str = "goal_planner_v1"

    def __post_init__(self) -> None:
        if not isinstance(self.goal_id, str) or not self.goal_id.strip():
            raise ValueError("goal_id cannot be empty.")
        if type(self.horizon_cycles) is not int or not 0 <= self.horizon_cycles <= 100000:
            raise ValueError(
                "horizon_cycles must be an integer between 0 and 100000."
            )
        _validate_optional_soh(self.target_soh, "target_soh")
        if (
            not isinstance(self.assessment_scope, str)
            or self.assessment_scope not in ASSESSMENT_SCOPES
        ):
            raise ValueError(
                "assessment_scope must be baseline_only, "
                "counterfactual_comparison, or auto."
            )
        validate_diagnostic_evidence(self.diagnostic_evidence)
        if not isinstance(self.goal_version, str) or not self.goal_version.strip():
            raise ValueError("goal_version cannot be empty.")
        if not isinstance(self.config_version, str) or not self.config_version.strip():
            raise ValueError("config_version cannot be empty.")

    def target_attainment(self, projected_soh: object) -> Optional[bool]:
        """Return None when no target was supplied; never invent a threshold."""
        if self.target_soh is None:
            return None
        _validate_optional_soh(projected_soh, "projected_soh")
        if projected_soh is None:
            raise ValueError("projected_soh is required when a target is configured.")
        return projected_soh >= self.target_soh

    def target_failure_requires_counterfactual(self) -> bool:
        """A missing target cannot be interpreted as a failed target."""
        return False
