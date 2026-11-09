"""Shared typed result contract for future experimental planner paths."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ToolExecutionOutcome:
    """Safe record of one allowlisted planner tool invocation."""

    tool_name: str
    status: str
    execution_order: int
    validated_arguments: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: Optional[dict[str, str]] = None

    def __post_init__(self) -> None:
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise ValueError("tool_name cannot be empty.")
        if self.status not in {
            "success", "unavailable", "invalid_arguments", "unknown_tool", "execution_failure", "invalid_result"
        }:
            raise ValueError("Unsupported tool execution status.")
        if type(self.execution_order) is not int or self.execution_order < 1:
            raise ValueError("execution_order must be a positive integer.")


@dataclass
class ExperimentalDecisionResult:
    """Result envelope with explicit unavailable and not-applicable states."""

    decision_id: str
    battery_id: str
    assessment_path: str
    termination_status: str
    goal_status: Optional[str] = None
    selected_action: Optional[str] = None
    available_evidence: list[Any] = field(default_factory=list)
    candidate_evaluations: list[dict[str, Any]] = field(default_factory=list)
    utility_ranking: Optional[dict[str, Any]] = None
    policy_comparison: dict[str, Any] = field(
        default_factory=lambda: {"status": "unavailable"}
    )
    explanation: list[str] = field(default_factory=list)
    snapshot_metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)
    tool_outcomes: list[ToolExecutionOutcome] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.decision_id, str) or not self.decision_id.strip():
            raise ValueError("decision_id cannot be empty.")
        if not isinstance(self.battery_id, str) or not self.battery_id.strip():
            raise ValueError("battery_id cannot be empty.")
        if not isinstance(self.assessment_path, str) or self.assessment_path not in {
            "baseline_only",
            "counterfactual_comparison",
        }:
            raise ValueError("Unsupported assessment_path.")
        if self.assessment_path == "baseline_only":
            if self.utility_ranking is not None:
                raise ValueError(
                    "Baseline-only results cannot contain intervention rankings."
                )
            if any(
                evaluation.get("scenario") != "No maintenance"
                for evaluation in self.candidate_evaluations
            ):
                raise ValueError(
                    "Baseline-only results can evaluate only the No maintenance baseline."
                )
            if self.selected_action not in (None, "no_intervention_selected"):
                raise ValueError(
                    "Baseline-only results cannot claim an intervention action."
                )
            if self.policy_comparison.get("status") != "not_applicable_baseline_only":
                raise ValueError(
                    "Baseline-only policy comparison must be explicitly not applicable."
                )
