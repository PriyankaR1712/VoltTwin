"""Deterministic offline comparison of held, periodic, and event policies."""

from __future__ import annotations

import math
from typing import Any

from backend.adaptive_decision_evaluator import choose_trigger, goal_fingerprint, validate_watermark
from digital_twin.goal_spec import GoalSpec


def _percentile95(values: list[int]) -> int | None:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)] if ordered else None


def _lag_summary(lags: list[int], eligible: int) -> dict[str, Any]:
    return {
        "mean_predictions": sum(lags) / len(lags) if lags else None,
        "p95_predictions": _percentile95(lags),
        "max_predictions": max(lags) if lags else None,
        "measured_events": len(lags),
        "events_without_prior_assessment": eligible - len(lags),
        "samples_predictions": lags,
    }


def _crossing_summary(crossings: list[int], calls: list[int]) -> dict[str, Any]:
    samples = []
    censored = []
    for crossing in crossings:
        call = next((count for count in calls if count >= crossing), None)
        row = {"crossing_prediction_count": crossing,
               "delay_predictions": None if call is None else call - crossing,
               "censored": call is None}
        (censored if call is None else samples).append(row)
    delays = [row["delay_predictions"] for row in samples]
    return {"crossings": len(crossings), "observed": len(samples),
            "censored": len(censored), "samples": samples + censored,
            "mean_delay_predictions": sum(delays) / len(delays) if delays else None,
            "p95_delay_predictions": _percentile95(delays),
            "max_delay_predictions": max(delays) if delays else None}


def _freshness_at_events(
    events: list[dict[str, Any]], call_indexes: list[int],
    actual_snapshot_watermarks: list[dict[str, int | None] | None] | None,
) -> dict[str, Any]:
    call_set = set(call_indexes)
    lags: list[int] = []
    last_event_count = None
    for index, event in enumerate(events):
        if index in call_set:
            last_event_count = event["watermark"]["prediction_count"]
        count = event["watermark"]["prediction_count"]
        if last_event_count is not None:
            lags.append(count - last_event_count)
    event_lag = _lag_summary(lags, len(events))
    if actual_snapshot_watermarks is None:
        snapshot_lag = {"available": False, "reason": "trigger-only replay does not execute Stage 3"}
    else:
        # Evaluate snapshot freshness at every timeline point, not just decision points.
        snapshot_lags: list[int] = []
        last_snapshot_count = None
        ahead_events = 0
        maximum_ahead = 0
        for index, event in enumerate(events):
            if index in call_set and actual_snapshot_watermarks[index] is not None:
                last_snapshot_count = actual_snapshot_watermarks[index]["prediction_count"]
            if last_snapshot_count is not None:
                raw_lag = event["watermark"]["prediction_count"] - last_snapshot_count
                if raw_lag < 0:
                    ahead_events += 1
                    maximum_ahead = max(maximum_ahead, -raw_lag)
                snapshot_lags.append(max(0, raw_lag))
        snapshot_lag = {"available": True, **_lag_summary(snapshot_lags, len(events)),
                        "events_snapshot_ahead_of_replay": ahead_events,
                        "maximum_snapshot_lead_predictions": maximum_ahead}
    return {"replay_event": event_lag, "actual_decision_snapshot": snapshot_lag}


def compare_reassessment_policies(
    events: list[dict[str, Any]], goal: GoalSpec, *, minimum_gap: int,
    epsilon_soh: float, periodic_gap: int | None = None,
    actual_snapshot_watermarks: dict[str, list[dict[str, Any] | None]] | None = None,
) -> dict[str, Any]:
    """Compare held, fixed-periodic, and event-triggered schedules.

    This is trigger-only replay. Optional snapshot arrays are real Stage 3
    snapshot watermarks aligned to event indexes and must be supplied from a
    separate integration replay; the function never fabricates them.
    """
    if periodic_gap is None:
        periodic_gap = minimum_gap
    if type(periodic_gap) is not int or periodic_gap < 1:
        raise ValueError("periodic_gap must be a positive integer")
    base_fingerprint, _ = goal_fingerprint(goal)
    normalized = []
    previous_count = -1
    for item in events:
        watermark = validate_watermark(item["watermark"])
        if watermark["prediction_count"] <= previous_count:
            raise ValueError("replay events must be strictly increasing")
        previous_count = watermark["prediction_count"]
        soh = item.get("predicted_soh")
        if soh is not None and (isinstance(soh, bool) or not isinstance(soh, (int, float)) or not math.isfinite(float(soh))):
            raise ValueError("predicted_soh must be finite numeric or null")
        event_goal = item.get("goal", goal)
        if isinstance(event_goal, dict):
            event_goal = GoalSpec(**event_goal)
        if not isinstance(event_goal, GoalSpec):
            raise ValueError("event goal must be a GoalSpec or GoalSpec object")
        computed_fingerprint = goal_fingerprint(event_goal)[0]
        event_fingerprint = item.get("goal_fingerprint", computed_fingerprint or base_fingerprint)
        if not isinstance(event_fingerprint, str) or not event_fingerprint:
            raise ValueError("goal_fingerprint must be a non-empty string")
        normalized.append({"watermark": watermark, "predicted_soh": soh, "goal": event_goal,
                           "goal_fingerprint": event_fingerprint,
                           "policy_version": item.get("policy_version", "replay-v1"),
                           "minimum_gap": item.get("minimum_gap", minimum_gap),
                           "epsilon_soh": item.get("epsilon_soh", epsilon_soh)})
    normalized_snapshots = None
    if actual_snapshot_watermarks is not None:
        normalized_snapshots = {}
        for policy, watermarks in actual_snapshot_watermarks.items():
            if policy not in {"held", "periodic", "adaptive"} or len(watermarks) != len(normalized):
                raise ValueError("actual snapshot watermark arrays must align with events and supported policies")
            normalized_snapshots[policy] = [None if wm is None else validate_watermark(wm) for wm in watermarks]

    periodic_indexes = []
    last_periodic_count = None
    adaptive_indexes = []
    actions = []
    previous = None
    reason_counts: dict[str, int] = {}
    for index, current in enumerate(normalized):
        count = current["watermark"]["prediction_count"]
        if count > 0 and (last_periodic_count is None or count - last_periodic_count >= periodic_gap):
            periodic_indexes.append(index)
            last_periodic_count = count
        trigger = choose_trigger(current=current, previous=previous, goal=current["goal"],
                                 minimum_gap=current["minimum_gap"], epsilon_soh=current["epsilon_soh"])
        if trigger["action"] == "reassess":
            adaptive_indexes.append(index)
            for reason in trigger["reasons"]:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        actions.append({"index": index, "watermark": current["watermark"],
                        "status": trigger["status"], "reasons": trigger["reasons"]})
        previous = {**current, "latched_side": trigger.get("latched_side"),
                    "decision_snapshot_watermark": current["watermark"] if trigger["action"] == "reassess" else (previous.get("decision_snapshot_watermark") if previous else None)}

    eligible_indexes = [i for i, item in enumerate(normalized) if item["watermark"]["prediction_count"] > 0]
    held_indexes = eligible_indexes[:1]
    crossings = [item["watermark"]["prediction_count"] for item in actions if "target_band_crossing" in item["reasons"]]
    adaptive_counts = [normalized[i]["watermark"]["prediction_count"] for i in adaptive_indexes]
    periodic_counts = [normalized[i]["watermark"]["prediction_count"] for i in periodic_indexes]
    held_counts = [normalized[i]["watermark"]["prediction_count"] for i in held_indexes]
    policies = {}
    for name, indexes, counts in (("held", held_indexes, held_counts), ("periodic", periodic_indexes, periodic_counts), ("adaptive", adaptive_indexes, adaptive_counts)):
        snapshots = normalized_snapshots.get(name) if normalized_snapshots is not None else None
        policies[name] = {"invocations": len(indexes), "invocation_indexes": indexes,
                          "freshness": _freshness_at_events(normalized, indexes, snapshots),
                          "crossing_detection_delay": _crossing_summary(crossings, counts)}
    return {"eligible_events": len(normalized), "periodic_gap": periodic_gap,
            "adaptive_invocations_by_reason": reason_counts, "policies": policies,
            "event_actions": actions, "target_band_crossings": len(crossings),
            "evaluation_kind": "trigger_policy_only_no_stage3_execution",
            "decision_quality_claim": False}


def sweep_development_thresholds(
    battery_sequences: dict[str, list[dict[str, Any]]], goal: GoalSpec, *,
    minimum_gaps: list[int], epsilon_values: list[float],
    actual_snapshot_watermarks: dict[str, dict[str, list[dict[str, Any] | None]]] | None = None,
) -> list[dict[str, Any]]:
    """Return a development-only Pareto comparison at matched call budgets.

    The nearest fixed-period schedule is selected by aggregate invocation
    count for each adaptive candidate. No threshold is selected or frozen.
    """
    if not battery_sequences:
        raise ValueError("At least one development battery is required")
    sequences = {key: battery_sequences[key] for key in sorted(battery_sequences)}

    def periodic_call_count(sequence, period):
        last = None
        count = 0
        for event in sequence:
            current = validate_watermark(event["watermark"])["prediction_count"]
            if current > 0 and (last is None or current - last >= period):
                count += 1
                last = current
        return count

    rows = []
    max_count = max((event["watermark"]["prediction_count"] for seq in sequences.values() for event in seq), default=1)
    for gap in minimum_gaps:
        for epsilon in epsilon_values:
            adaptive_reports = {key: compare_reassessment_policies(
                seq, goal, minimum_gap=gap, epsilon_soh=epsilon, periodic_gap=max_count + 1,
                actual_snapshot_watermarks=(actual_snapshot_watermarks or {}).get(key),
            ) for key, seq in sequences.items()}
            adaptive_calls = sum(report["policies"]["adaptive"]["invocations"] for report in adaptive_reports.values())
            # Search the fixed-period call-count curve and choose the closest budget.
            periodic_budget = {period: sum(periodic_call_count(seq, period) for seq in sequences.values())
                               for period in range(1, max_count + 2)}
            matched_gap = min(periodic_budget, key=lambda period: (abs(periodic_budget[period] - adaptive_calls), period))
            periodic_reports = {key: compare_reassessment_policies(
                seq, goal, minimum_gap=gap, epsilon_soh=epsilon, periodic_gap=matched_gap,
                actual_snapshot_watermarks=(actual_snapshot_watermarks or {}).get(key),
            ) for key, seq in sequences.items()}
            all_lags = {policy: {"replay_event": [], "actual_decision_snapshot": []}
                        for policy in ("held", "periodic", "adaptive")}
            all_crossings = {policy: [] for policy in all_lags}
            invocations = {policy: 0 for policy in all_lags}
            reason_counts: dict[str, int] = {}
            for key in sequences:
                for policy, report in (("held", periodic_reports[key]),
                                       ("periodic", periodic_reports[key]),
                                       ("adaptive", adaptive_reports[key])):
                    stats = report["policies"][policy]
                    invocations[policy] += stats["invocations"]
                    all_lags[policy]["replay_event"].extend(stats["freshness"]["replay_event"]["samples_predictions"])
                    snapshot_stats = stats["freshness"]["actual_decision_snapshot"]
                    if snapshot_stats.get("available"):
                        all_lags[policy]["actual_decision_snapshot"].extend(snapshot_stats["samples_predictions"])
                    all_crossings[policy].extend(stats["crossing_detection_delay"]["samples"])
                for reason, count in adaptive_reports[key]["adaptive_invocations_by_reason"].items():
                    reason_counts[reason] = reason_counts.get(reason, 0) + count
            freshness = {policy: {
                "replay_event": _lag_summary(samples["replay_event"], sum(len(seq) for seq in sequences.values())),
                "actual_decision_snapshot": ({"available": True, **_lag_summary(samples["actual_decision_snapshot"], sum(len(seq) for seq in sequences.values()))}
                    if actual_snapshot_watermarks is not None and samples["actual_decision_snapshot"] else
                    {"available": False, "reason": "trigger-only replay does not execute Stage 3"}),
            } for policy, samples in all_lags.items()}
            crossing_summary = {}
            for policy, samples in all_crossings.items():
                delays = [sample["delay_predictions"] for sample in samples if not sample["censored"]]
                crossing_summary[policy] = {"crossings": len(samples), "observed": len(delays),
                    "censored": sum(sample["censored"] for sample in samples),
                    "mean_delay_predictions": sum(delays) / len(delays) if delays else None,
                    "p95_delay_predictions": _percentile95(delays),
                    "max_delay_predictions": max(delays) if delays else None}
            rows.append({
                "minimum_gap": gap, "epsilon_soh": epsilon,
                "development_batteries": list(sequences),
                "eligible_events": sum(len(seq) for seq in sequences.values()),
                "matched_periodic_gap": matched_gap,
                "invocations": invocations,
                "adaptive_minus_periodic_invocations": invocations["adaptive"] - invocations["periodic"],
                "freshness": freshness, "crossing_detection_delay": crossing_summary,
                "adaptive_invocations_by_reason": reason_counts,
                "actual_decision_snapshot_freshness": "provided_integration_trace" if actual_snapshot_watermarks is not None else "unavailable_without_stage3_integration_trace",
                "decision_quality_claim": False,
                "evaluation_kind": "development_trigger_policy_replay_no_stage3_execution",
            })
    return sorted(rows, key=lambda row: (row["invocations"]["adaptive"], row["minimum_gap"], row["epsilon_soh"]))
