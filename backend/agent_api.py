"""HTTP API for the existing goal-directed Agentic AI workflow."""

from datetime import datetime, timezone
import math
import os
from threading import Lock
from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.decision_history_serializer import freeze_decision_payload
from backend.decision_history_store import DecisionHistoryStore, decode_cursor
from backend.twin_registry import twin_registry
from digital_twin.goal_directed_orchestrator import run_goal_directed_orchestrator
from digital_twin.decision_models import ExperimentalDecisionResult
from digital_twin.goal_spec import GoalSpec
from backend.adaptive_decision_service import AdaptiveDecisionService
from backend.adaptive_evaluation_store import AdaptiveEvaluationStore

router = APIRouter(prefix="/api/agent", tags=["Agentic AI"])
_history_store: Optional[DecisionHistoryStore] = None
_history_store_lock = Lock()
_adaptive_service: Optional[AdaptiveDecisionService] = None
_adaptive_service_lock = Lock()


def _get_history_store() -> DecisionHistoryStore:
    global _history_store
    if _history_store is None:
        with _history_store_lock:
            if _history_store is None:
                _history_store = DecisionHistoryStore()
    return _history_store


def _get_adaptive_service() -> AdaptiveDecisionService:
    global _adaptive_service
    if _adaptive_service is None:
        with _adaptive_service_lock:
            if _adaptive_service is None:
                path = os.environ.get("VOLTTWIN_ADAPTIVE_DB_PATH")
                minimum_gap = os.environ.get("VOLTTWIN_ADAPTIVE_MINIMUM_GAP")
                epsilon_soh = os.environ.get("VOLTTWIN_ADAPTIVE_EPSILON_SOH")
                policy_version = os.environ.get("VOLTTWIN_ADAPTIVE_POLICY_VERSION")
                if minimum_gap is None or epsilon_soh is None or not policy_version:
                    raise RuntimeError("Frozen adaptive policy configuration is not set.")
                try:
                    configured_gap = int(minimum_gap)
                    configured_epsilon = float(epsilon_soh)
                except (TypeError, ValueError, OverflowError) as exc:
                    raise RuntimeError("Frozen adaptive policy configuration is invalid.") from exc
                if configured_gap < 1 or not math.isfinite(configured_epsilon) or not 0 <= configured_epsilon < 1:
                    raise RuntimeError("Frozen adaptive policy configuration is invalid.")
                _adaptive_service = AdaptiveDecisionService(
                    store=AdaptiveEvaluationStore(path) if path else AdaptiveEvaluationStore(),
                    minimum_gap=configured_gap,
                    epsilon_soh=configured_epsilon,
                    policy_version=policy_version,
                )
    return _adaptive_service


def initialize_adaptive_service_if_configured() -> None:
    """Acquire the adaptive database worker lease during application startup.

    An unset policy keeps the feature opt-in. Partial configuration fails
    startup rather than activating a process with ambiguous recovery state.
    """
    config_keys = (
        "VOLTTWIN_ADAPTIVE_MINIMUM_GAP",
        "VOLTTWIN_ADAPTIVE_EPSILON_SOH",
        "VOLTTWIN_ADAPTIVE_POLICY_VERSION",
    )
    if any(os.environ.get(key) is not None for key in config_keys):
        _get_adaptive_service()


def _record_plan_in_memory(state: dict[str, Any], plan: tuple[str, ...]) -> None:
    """Replace plan evidence with the latest complete in-memory plan."""
    state["available"] = False
    state["tools"] = None
    state["tools"] = tuple(plan)
    state["available"] = True


class AgentDecisionRequest(BaseModel):
    """Request envelope around the existing validated GoalSpec."""

    model_config = ConfigDict(extra="forbid")

    battery_id: str = Field(min_length=1, max_length=100, strict=True)
    goal: GoalSpec

    @field_validator("battery_id")
    @classmethod
    def validate_battery_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Battery ID cannot be empty.")
        return value

    @field_validator("goal", mode="before")
    @classmethod
    def construct_goal_spec(cls, value):
        if isinstance(value, GoalSpec):
            return value
        if not isinstance(value, dict):
            raise ValueError("goal must be a goal specification object.")
        try:
            return GoalSpec(**value)
        except (TypeError, ValueError) as exc:
            raise ValueError(str(exc)) from exc


class AdaptiveWatermarkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prediction_count: int = Field(ge=0, strict=True)
    version: int = Field(ge=0, strict=True)
    observation_index: Optional[int] = Field(default=None, ge=0, strict=True)


class AdaptiveDecisionRequest(AgentDecisionRequest):
    event_watermark: AdaptiveWatermarkRequest


class DecisionSummaryResponse(BaseModel):
    decision_id: str
    battery_id: str
    created_at: str
    decision_status: Literal["completed", "incomplete", "failed"]
    termination_status: str
    goal_id: str


class DecisionListResponse(BaseModel):
    items: list[DecisionSummaryResponse]
    next_cursor: Optional[str]
    has_more: bool


class DecisionToolOutcomeResponse(BaseModel):
    outcome_id: int
    tool_name: str
    planned: Optional[bool]
    executed: bool
    execution_order: int
    status: str
    validated_arguments: Optional[dict[str, Any]]
    result_summary: Any
    error_details: Optional[dict[str, Any]]


class DecisionScenarioResponse(BaseModel):
    scenario_id: int
    scenario_type: str
    scenario_name: str
    projected_soh: float
    utility: Optional[float]
    feasibility: Any
    result_data: dict[str, Any]


class DecisionDetailResponse(BaseModel):
    decision_id: str
    battery_id: str
    created_at_utc: str
    goal_spec: dict[str, Any]
    goal_id: str
    horizon_cycles: int
    target_soh: Optional[float]
    assessment_scope: str
    diagnostic_evidence: Optional[dict[str, Any]]
    goal_version: str
    config_version: str
    result: dict[str, Any]
    snapshot_metadata: Any
    baseline_result: Any
    counterfactual_result: Any
    utility_ranking: Any
    feasibility: Any
    planned_tools: Optional[list[str]]
    plan_evidence_available: bool
    executed_tools: list[dict[str, Any]]
    final_decision: dict[str, Any]
    termination_status: str
    decision_status: Literal["completed", "incomplete", "failed"]
    explanation: list[str]
    failure_details: dict[str, Any]
    payload_digest: str
    record_version: int
    tool_outcomes: list[DecisionToolOutcomeResponse]
    scenarios: list[DecisionScenarioResponse]


@router.post("/decide", response_model=ExperimentalDecisionResult)
def decide(request: AgentDecisionRequest):
    """Run one decision against the registered twin's atomic snapshot.

    A synchronous FastAPI route runs in the framework's worker pool, so
    snapshot capture, prediction-history checks and simulation do not block
    the asynchronous event loop.
    """
    result, persistence_status, status_code = _run_and_persist_decision(
        request.battery_id, request.goal
    )
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(result),
        headers={"X-Decision-Persistence-Status": persistence_status},
    )


def _run_and_persist_decision(
    battery_id: str, goal: GoalSpec, captured_snapshot: Optional[dict[str, Any]] = None
):
    """Run Stage 3 once and persist its immutable Stage 4 record once."""
    try:
        twin_registry.get(battery_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    plan_state: dict[str, Any] = {"available": False, "tools": None}

    def record_plan(plan: tuple[str, ...]) -> None:
        _record_plan_in_memory(plan_state, plan)

    decision_started_at = datetime.now(timezone.utc)
    result = run_goal_directed_orchestrator(
        battery_id=battery_id,
        goal=goal,
        twin_registry=twin_registry,
        plan_recorder=record_plan,
        captured_snapshot=captured_snapshot,
    )

    status_code = 200
    if result.termination_status == "invalid_goal":
        status_code = 422
    elif result.termination_status == "invalid_snapshot":
        status_code = 409
    elif result.termination_status in {
        "service_failure",
        "invalid_service_result",
        "invalid_scenario_evidence",
    }:
        status_code = 500

    persistence_status = "failed"
    try:
        payload = freeze_decision_payload(
            goal=goal,
            result=result,
            decision_started_at=decision_started_at,
            planned_tools=plan_state["tools"],
            plan_evidence_available=plan_state["available"],
        )
        persistence_status = _get_history_store().save(payload)
        if persistence_status not in {
            "saved",
            "already_saved",
            "idempotency_conflict",
        }:
            persistence_status = "failed"
    except Exception:
        # Persistence is auxiliary: never alter the Stage 3 response or rerun it.
        persistence_status = "failed"

    return result, persistence_status, status_code


@router.post("/adaptive-decide")
def adaptive_decide(request: AdaptiveDecisionRequest):
    """Opt-in observation-event-triggered decision reassessment."""
    try:
        service = _get_adaptive_service()
        response = service.evaluate(
            battery_id=request.battery_id,
            goal=request.goal,
            event_watermark=request.event_watermark.model_dump(),
            twin_registry=twin_registry,
            run_decision=lambda captured_snapshot: _run_and_persist_decision(
                request.battery_id, request.goal, captured_snapshot=captured_snapshot
            ),
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Adaptive evaluation is unavailable or indeterminate.",
        ) from exc
    headers = {}
    persistence_status = response.get("decision_persistence_status")
    if persistence_status in {"saved", "already_saved", "failed", "idempotency_conflict"}:
        headers["X-Decision-Persistence-Status"] = persistence_status
    status_code = response.get("decision_http_status", 200)
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response),
        headers=headers,
    )


@router.get("/batteries/{battery_id}/decisions", response_model=DecisionListResponse)
def list_battery_decisions(
    battery_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: Optional[str] = Query(default=None),
):
    try:
        decode_cursor(cursor)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid pagination cursor.") from exc
    try:
        return _get_history_store().list_decisions(
            battery_id=battery_id,
            limit=limit,
            cursor=cursor,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Decision history is unavailable.",
        ) from exc


@router.get("/decisions/{decision_id}", response_model=DecisionDetailResponse)
def get_decision(decision_id: str):
    try:
        record = _get_history_store().get_decision(decision_id)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Decision history is unavailable.",
        ) from exc
    if record is None:
        raise HTTPException(status_code=404, detail="Decision not found.")
    return record
