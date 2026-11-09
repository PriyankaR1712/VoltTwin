"""HTTP API for the existing goal-directed Agentic AI workflow."""

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.twin_registry import twin_registry
from digital_twin.goal_directed_orchestrator import run_goal_directed_orchestrator
from digital_twin.decision_models import ExperimentalDecisionResult
from digital_twin.goal_spec import GoalSpec

router = APIRouter(prefix="/api/agent", tags=["Agentic AI"])


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

    result = run_goal_directed_orchestrator(
        battery_id=request.battery_id,
        goal=request.goal,
        twin_registry=twin_registry,
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

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(result),
    )
