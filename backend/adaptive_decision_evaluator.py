"""Deterministic, evidence-gated adaptive reassessment policy.

This module evaluates event watermarks only. It never executes decision tools.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict
from typing import Any

from digital_twin.goal_spec import GoalSpec


def goal_fingerprint(goal: GoalSpec) -> tuple[str, bytes]:
    """Validate and fingerprint every GoalSpec field with stable JSON bytes."""
    validated = GoalSpec(**asdict(goal))
    data = asdict(validated)
    if data["target_soh"] is not None:
        data["target_soh"] = float(data["target_soh"])
    encoded = json.dumps(
        {"version": "goal-fingerprint-v1", "goal": data},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest(), encoded


def validate_watermark(value: Any) -> dict[str, int | None]:
    if not isinstance(value, dict):
        raise ValueError("watermark must be an object")
    if set(value) != {"prediction_count", "version", "observation_index"}:
        raise ValueError("watermark must contain exactly the supported fields")
    out: dict[str, int | None] = {}
    for key in ("prediction_count", "version", "observation_index"):
        item = value[key]
        if item is None and key == "observation_index":
            out[key] = None
        elif type(item) is not int or item < 0:
            raise ValueError(f"{key} must be a non-negative integer")
        else:
            out[key] = item
    if out["version"] != out["prediction_count"]:
        raise ValueError("version and prediction_count are inconsistent")
    return out


def choose_trigger(
    *,
    current: dict[str, Any],
    previous: dict[str, Any] | None,
    goal: GoalSpec,
    minimum_gap: int,
    epsilon_soh: float,
) -> dict[str, Any]:
    """Return a deterministic hold/reassess decision for a validated state."""
    if type(minimum_gap) is not int or minimum_gap < 1:
        raise ValueError("minimum_gap must be a positive integer")
    if isinstance(epsilon_soh, bool) or not isinstance(epsilon_soh, (int, float)):
        raise ValueError("epsilon_soh must be finite and in [0, 1)")
    epsilon = float(epsilon_soh)
    if not math.isfinite(epsilon) or not 0 <= epsilon < 1:
        raise ValueError("epsilon_soh must be finite and in [0, 1)")

    watermark = validate_watermark(current["watermark"])
    prior_watermark = validate_watermark(previous["watermark"]) if previous else None
    if watermark["prediction_count"] == 0:
        return {"action": "hold", "status": "not_ready", "reasons": ["no_prediction"]}
    if previous is None:
        return {"action": "reassess", "status": "reassess", "reasons": ["first_assessment"], "latched_side": _side(current.get("predicted_soh"), goal.target_soh, epsilon)}

    if current.get("goal_fingerprint") != previous.get("goal_fingerprint"):
        return {"action": "reassess", "status": "reassess", "reasons": ["goal_changed"], "latched_side": _side(current.get("predicted_soh"), goal.target_soh, epsilon)}
    if any(current.get(key) != previous.get(key) for key in ("policy_version", "minimum_gap", "epsilon_soh")):
        return {"action": "reassess", "status": "reassess", "reasons": ["policy_configuration_changed"], "latched_side": _side(current.get("predicted_soh"), goal.target_soh, epsilon)}

    if watermark == prior_watermark:
        return {"action": "hold", "status": "duplicate", "reasons": ["duplicate_watermark"], "latched_side": previous.get("latched_side")}
    if watermark["prediction_count"] < prior_watermark["prediction_count"] or (
        prior_watermark["observation_index"] is not None
        and watermark["observation_index"] is not None
        and watermark["observation_index"] <= prior_watermark["observation_index"]
    ):
        return {"action": "reject", "status": "stale_event", "reasons": ["out_of_order_watermark"]}
    if watermark["prediction_count"] != watermark["version"]:
        return {"action": "reassess", "status": "discontinuity", "reasons": ["inconsistent_watermark"]}
    old_side = previous.get("latched_side")
    observed_side = _side(current.get("predicted_soh"), goal.target_soh, epsilon)
    new_side = observed_side or old_side
    if old_side is not None and observed_side is not None and old_side != observed_side:
        return {"action": "reassess", "status": "reassess", "reasons": ["target_band_crossing"], "latched_side": observed_side}
    baseline_count = previous.get("decision_snapshot_watermark", {}).get("prediction_count")
    if type(baseline_count) is not int or baseline_count < 0:
        return {"action": "reassess", "status": "reassess", "reasons": ["assessment_watermark_unavailable"], "latched_side": new_side}
    if watermark["prediction_count"] - baseline_count >= minimum_gap:
        return {"action": "reassess", "status": "reassess", "reasons": ["minimum_observation_gap"], "latched_side": new_side}
    return {"action": "hold", "status": "held", "reasons": ["minimum_gap_not_met"], "latched_side": new_side}


def _side(predicted_soh: Any, target_soh: Any, epsilon: float) -> str | None:
    if target_soh is None or isinstance(predicted_soh, bool) or not isinstance(predicted_soh, (int, float)):
        return None
    soh = float(predicted_soh)
    if not math.isfinite(soh):
        return None
    margin = soh - float(target_soh)
    if margin >= epsilon:
        return "above"
    if margin <= -epsilon:
        return "below"
    return None
