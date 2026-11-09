"""HTTP API for the existing goal-directed Agentic AI workflow."""

from datetime import datetime, timezone
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

router = APIRouter(prefix="/api/agent", tags=["Agentic AI"])
_history_store: Optional[DecisionHistoryStore] = None
_history_store_lock = Lock()


def _get_history_store() -> DecisionHistoryStore:
    global _history_store
    if _history_store is None:
        with _history_store_lock:
            if _history_store is None:
                _history_store = DecisionHistoryStore()
    return _history_store


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
    try:
        twin_registry.get(request.battery_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    plan_state: dict[str, Any] = {"available": False, "tools": None}

    def record_plan(plan: tuple[str, ...]) -> None:
        _record_plan_in_memory(plan_state, plan)

    decision_started_at = datetime.now(timezone.utc)
    result = run_goal_directed_orchestrator(
        battery_id=request.battery_id,
        goal=request.goal,
        twin_registry=twin_registry,
        plan_recorder=record_plan,
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
            goal=request.goal,
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

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(result),
        headers={"X-Decision-Persistence-Status": persistence_status},
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
