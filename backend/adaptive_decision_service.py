"""Coordinates adaptive event evaluation with existing Stage 3/4 workflows."""

from __future__ import annotations

import hashlib
import json
import math
import threading
import uuid
import weakref
from dataclasses import asdict
from typing import Any, Callable

from backend.adaptive_decision_evaluator import choose_trigger, goal_fingerprint, validate_watermark
from backend.adaptive_evaluation_store import AdaptiveEvaluationStore
from digital_twin.goal_spec import GoalSpec


class AdaptiveDecisionService:
    """Single-process adaptive coordinator; SQLite records durable event receipts."""

    def __init__(self, store: AdaptiveEvaluationStore | None = None,
                 *, minimum_gap: int, epsilon_soh: float,
                 policy_version: str):
        if type(minimum_gap) is not int or minimum_gap < 1:
            raise RuntimeError("Frozen minimum-gap policy is invalid.")
        if isinstance(epsilon_soh, bool) or not isinstance(epsilon_soh, (int, float)) or not math.isfinite(float(epsilon_soh)) or not 0 <= float(epsilon_soh) < 1:
            raise RuntimeError("Frozen SOH hysteresis policy is invalid.")
        if not isinstance(policy_version, str) or not policy_version.strip():
            raise RuntimeError("Frozen adaptive policy version is invalid.")
        self.store = store or AdaptiveEvaluationStore()
        self.minimum_gap = minimum_gap
        self.epsilon_soh = epsilon_soh
        self.policy_version = policy_version
        self._process_id = str(uuid.uuid4())
        self._manager_generations: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
        self._generation_lock = threading.Lock()
        self._battery_locks: dict[str, threading.RLock] = {}
        self._locks_guard = threading.Lock()

    def _generation(self, manager: Any) -> str:
        with self._generation_lock:
            generation = self._manager_generations.get(manager)
            if generation is None:
                generation = f"{self._process_id}:{uuid.uuid4()}"
                self._manager_generations[manager] = generation
            return generation

    def _lock_for(self, battery_id: str) -> threading.RLock:
        with self._locks_guard:
            return self._battery_locks.setdefault(battery_id, threading.RLock())

    def evaluate(self, *, battery_id: str, goal: GoalSpec, event_watermark: dict,
                 twin_registry: Any,
                 run_decision: Callable[[dict[str, Any]], tuple[Any, str, int]]) -> dict:
        """Validate one event and invoke Stage 3 at most once for its event key."""
        with self._lock_for(battery_id):
            manager = twin_registry.get(battery_id)
            event_snapshot = manager.get_snapshot()
            state = event_snapshot.get("state") if isinstance(event_snapshot, dict) else None
            if not isinstance(state, dict):
                raise ValueError("Registered Twin returned an invalid event snapshot.")
            current_watermark = validate_watermark({
                "prediction_count": state.get("prediction_count"),
                "version": event_snapshot.get("version"),
                "observation_index": state.get("last_observation_index"),
            })
            requested = validate_watermark(event_watermark)
            if requested != current_watermark:
                raise ValueError("Observation event watermark is stale or does not match the registered Twin.")
            predicted_soh = state.get("twin_state", {}).get("soh")
            if isinstance(predicted_soh, bool) or not isinstance(predicted_soh, (int, float)) or not math.isfinite(float(predicted_soh)):
                predicted_soh = None
            generation = self._generation(manager)
            fingerprint, _ = goal_fingerprint(goal)
            unresolved = self.store.find_unresolved(battery_id, fingerprint, current_watermark)
            if unresolved is not None:
                if unresolved["status"] == "in_progress":
                    self.store.mark_indeterminate(unresolved["event_key"])
                return {
                    "evaluation_status": "indeterminate",
                    "decision_id": unresolved.get("decision_id"),
                    "event_watermark": current_watermark,
                    "decision_snapshot_watermark": unresolved.get("decision_snapshot_watermark"),
                    "trigger_reasons": unresolved["trigger_reasons"],
                }
            previous_row = self.store.get_latest(battery_id, generation)
            previous = None
            if previous_row is not None:
                previous = {
                    "watermark": previous_row["event_watermark"],
                    "goal_fingerprint": previous_row["goal_fingerprint"],
                    "decision_snapshot_watermark": previous_row["decision_snapshot_watermark"],
                    "latched_side": previous_row["latched_side"],
                    "policy_version": previous_row["policy_version"],
                    "minimum_gap": previous_row["minimum_gap"],
                    "epsilon_soh": previous_row["epsilon_soh"],
                }
            current = {
                "watermark": current_watermark,
                "predicted_soh": predicted_soh,
                "goal_fingerprint": fingerprint,
                "policy_version": self.policy_version,
                "minimum_gap": self.minimum_gap,
                "epsilon_soh": self.epsilon_soh,
            }
            trigger = choose_trigger(
                current=current, previous=previous, goal=goal,
                minimum_gap=self.minimum_gap, epsilon_soh=self.epsilon_soh,
            )
            event_body = json.dumps(
                [battery_id, generation, fingerprint, current_watermark],
                sort_keys=True, separators=(",", ":"), allow_nan=False,
            ).encode("utf-8")
            event_key = hashlib.sha256(b"adaptive-event-v1:" + event_body).hexdigest()
            reserve_id, existing = self.store.reserve(
                event_key=event_key, battery_id=battery_id, generation_id=generation,
                goal_fingerprint=fingerprint, goal_spec=asdict(goal),
                event_watermark=current_watermark, predicted_soh=predicted_soh,
                minimum_gap=self.minimum_gap, epsilon_soh=self.epsilon_soh,
                policy_version=self.policy_version,
                prior_decision_id=self.store.get_latest_decision_id(battery_id, generation),
            )
            if existing is not None:
                status = existing["status"]
                if status == "in_progress":
                    self.store.mark_indeterminate(event_key)
                    status = "indeterminate"
                if status == "indeterminate":
                    return {"evaluation_status": "indeterminate", "decision_id": existing.get("decision_id"),
                            "event_watermark": current_watermark,
                            "decision_snapshot_watermark": existing.get("decision_snapshot_watermark")}
                return {"evaluation_status": status, "decision_id": existing.get("decision_id"),
                        "event_watermark": current_watermark,
                        "decision_snapshot_watermark": existing.get("decision_snapshot_watermark"),
                        "trigger_reasons": json.loads(existing["trigger_reasons_json"]),
                        "decision_persistence_status": existing.get("stage4_persistence_status")}

            if trigger["status"] == "stale_event":
                status = "stale_event"
                self.store.finish(reserve_id, status=status, reasons=trigger["reasons"],
                                  latched_side=trigger.get("latched_side"),
                                  decision_snapshot_watermark=previous["decision_snapshot_watermark"] if previous else None)
                return {"evaluation_status": status, "event_watermark": current_watermark,
                        "decision_snapshot_watermark": previous["decision_snapshot_watermark"] if previous else None,
                        "trigger_reasons": trigger["reasons"]}
            if trigger["action"] == "hold":
                status = "not_ready" if trigger["status"] == "not_ready" else "held"
                self.store.finish(reserve_id, status=status, reasons=trigger["reasons"],
                                  latched_side=trigger.get("latched_side"),
                                  decision_snapshot_watermark=previous["decision_snapshot_watermark"] if previous else None)
                return {"evaluation_status": status, "event_watermark": current_watermark,
                        "decision_snapshot_watermark": previous["decision_snapshot_watermark"] if previous else None,
                        "trigger_reasons": trigger["reasons"]}

            try:
                result, persistence_status, http_status = run_decision(event_snapshot)
            except BaseException:
                # Stage 3 may already have executed. Never retry this reserved key.
                self.store.finish(reserve_id, status="indeterminate", reasons=["decision_execution_interrupted"],
                                  latched_side=trigger.get("latched_side"))
                raise
            snapshot = result.snapshot_metadata or {}
            decision_watermark = {
                "version": snapshot.get("snapshot_version", snapshot.get("version")),
                "prediction_count": snapshot.get("prediction_count"),
                "observation_index": snapshot.get("observation_index"),
            }
            try:
                decision_watermark = validate_watermark(decision_watermark)
            except ValueError:
                decision_watermark = None
            self.store.finish(
                reserve_id, status="reassessed", reasons=trigger["reasons"],
                latched_side=trigger.get("latched_side"), decision_id=result.decision_id,
                persistence_status=persistence_status,
                decision_snapshot_watermark=decision_watermark,
            )
            return {
                "evaluation_status": "reassessed", "trigger_reasons": trigger["reasons"],
                "event_watermark": current_watermark,
                "decision_snapshot_watermark": decision_watermark,
                "decision_id": result.decision_id,
                "decision_persistence_status": persistence_status,
                "decision_http_status": http_status,
                "decision_result": result,
            }
