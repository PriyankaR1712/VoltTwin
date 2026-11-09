"""SQLite persistence for immutable Agentic AI decision history payloads."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sqlite3
import time
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from backend.decision_history_serializer import FrozenDecisionPayload


SCHEMA_VERSION = 1
_MAX_SAVE_ATTEMPTS = 3
_CURSOR_RE = re.compile(r"^[A-Za-z0-9_-]+$")


@dataclass(frozen=True)
class _PreparedPayload:
    """DB parameters prepared once and reused for every transient retry."""

    database_json: bytes
    payload_digest: str
    decision_values: tuple[Any, ...]
    tool_rows: tuple[tuple[Any, ...], ...]
    scenario_rows: tuple[tuple[Any, ...], ...]


def _json_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def encode_cursor(created_at_utc: str, decision_id: str) -> str:
    body = json.dumps(
        [created_at_utc, decision_id], separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return base64.urlsafe_b64encode(body).decode("ascii").rstrip("=")


def decode_cursor(cursor: Optional[str]) -> Optional[tuple[str, str]]:
    if cursor is None:
        return None
    if not isinstance(cursor, str) or not cursor or not _CURSOR_RE.fullmatch(cursor):
        raise ValueError("Invalid pagination cursor.")
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
    except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid pagination cursor.") from exc
    if (
        not isinstance(decoded, list)
        or len(decoded) != 2
        or not all(isinstance(item, str) and item for item in decoded)
    ):
        raise ValueError("Invalid pagination cursor.")
    try:
        datetime.strptime(decoded[0], "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as exc:
        raise ValueError("Invalid pagination cursor.") from exc
    return decoded[0], decoded[1]


class DecisionHistoryStore:
    """Own an isolated SQLite file and its atomic decision-history operations."""

    def __init__(self, database_path: Optional[str | Path] = None):
        self.database_path = Path(database_path) if database_path else (
            Path(__file__).resolve().parents[1] / "data" / "decision_history.db"
        )
        self.initialize_schema()

    def _connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path, timeout=0.1)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize_schema(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, SCHEMA_VERSION):
                connection.rollback()
                raise RuntimeError("Unsupported decision history schema version.")
            if version == SCHEMA_VERSION:
                connection.commit()
                return
            statements = (
                """CREATE TABLE decision_records (
                    decision_id TEXT PRIMARY KEY,
                    battery_id TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL,
                    goal_spec_json TEXT NOT NULL,
                    goal_id TEXT NOT NULL,
                    horizon_cycles INTEGER NOT NULL,
                    target_soh REAL,
                    assessment_scope TEXT NOT NULL,
                    diagnostic_evidence_json TEXT,
                    goal_version TEXT NOT NULL,
                    config_version TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    snapshot_metadata_json TEXT,
                    baseline_result_json TEXT,
                    counterfactual_result_json TEXT,
                    utility_ranking_json TEXT,
                    feasibility_json TEXT,
                    planned_tools_json TEXT,
                    plan_evidence_available INTEGER NOT NULL,
                    executed_tools_json TEXT NOT NULL,
                    final_decision_json TEXT NOT NULL,
                    termination_status TEXT NOT NULL,
                    decision_status TEXT NOT NULL
                        CHECK(decision_status IN ('completed', 'incomplete', 'failed')),
                    explanation_json TEXT NOT NULL,
                    failure_details_json TEXT NOT NULL,
                    payload_digest TEXT NOT NULL,
                    record_version INTEGER NOT NULL
                )""",
                """CREATE INDEX idx_decision_records_battery_created
                    ON decision_records(battery_id, created_at_utc DESC, decision_id DESC)""",
                """CREATE INDEX idx_decision_records_created
                    ON decision_records(created_at_utc DESC, decision_id DESC)""",
                """CREATE TABLE decision_tool_outcomes (
                    outcome_id INTEGER PRIMARY KEY,
                    decision_id TEXT NOT NULL REFERENCES decision_records(decision_id)
                        ON DELETE CASCADE,
                    tool_name TEXT NOT NULL,
                    planned INTEGER,
                    executed INTEGER NOT NULL CHECK(executed IN (0, 1)),
                    execution_order INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    validated_arguments_json TEXT,
                    result_summary_json TEXT,
                    error_details_json TEXT,
                    UNIQUE(decision_id, execution_order)
                )""",
                """CREATE INDEX idx_tool_outcomes_decision_order
                    ON decision_tool_outcomes(decision_id, execution_order)""",
                """CREATE TABLE decision_scenarios (
                    scenario_id INTEGER PRIMARY KEY,
                    decision_id TEXT NOT NULL REFERENCES decision_records(decision_id)
                        ON DELETE CASCADE,
                    scenario_type TEXT NOT NULL,
                    scenario_name TEXT NOT NULL,
                    projected_soh REAL NOT NULL,
                    utility REAL,
                    feasibility_json TEXT,
                    result_data_json TEXT NOT NULL,
                    UNIQUE(decision_id, scenario_name)
                )""",
                """CREATE INDEX idx_decision_scenarios_decision
                    ON decision_scenarios(decision_id)""",
            )
            try:
                for statement in statements:
                    connection.execute(statement)
                connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    @staticmethod
    def _prepare(payload: FrozenDecisionPayload) -> _PreparedPayload:
        if hashlib.sha256(payload.canonical_digest_bytes).hexdigest() != payload.payload_digest:
            raise ValueError("Frozen payload canonical digest is inconsistent.")
        try:
            data = json.loads(payload.database_json)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("Frozen decision payload is invalid JSON.") from exc
        if data.get("decision_id") != payload.decision_id:
            raise ValueError("Frozen payload decision ID is inconsistent.")
        if data.get("payload_digest") != payload.payload_digest:
            raise ValueError("Frozen payload digest is inconsistent.")
        goal = data["goal_fields"]
        values = (
            data["decision_id"],
            data["battery_id"],
            data["created_at_utc"],
            _json_text(data["goal_spec"]),
            goal["goal_id"],
            goal["horizon_cycles"],
            goal["target_soh"],
            goal["assessment_scope"],
            _json_text(goal["diagnostic_evidence"]),
            goal["goal_version"],
            goal["config_version"],
            _json_text(data["result"]),
            _json_text(data["snapshot_metadata"]),
            _json_text(data["baseline_result"]),
            _json_text(data["counterfactual_result"]),
            _json_text(data["utility_ranking"]),
            _json_text(data["feasibility"]),
            _json_text(data["planned_tools"]),
            int(data["plan_evidence_available"]),
            _json_text(data["executed_tools"]),
            _json_text(data["final_decision"]),
            data["termination_status"],
            data["decision_status"],
            _json_text(data["explanation"]),
            _json_text(data["failure_details"]),
            payload.payload_digest,
            data["record_version"],
        )
        tools = tuple(
            (
                data["decision_id"],
                row["tool_name"],
                None if row["planned"] is None else int(row["planned"]),
                int(row["executed"]),
                row["execution_order"],
                row["status"],
                _json_text(row["validated_arguments"]),
                _json_text(row["result_summary"]),
                _json_text(row["error_details"]),
            )
            for row in data["tool_outcomes"]
        )
        scenarios = tuple(
            (
                data["decision_id"],
                row["scenario_type"],
                row["scenario_name"],
                row["projected_soh"],
                row["utility"],
                _json_text(row["feasibility"]),
                _json_text(row["result_data"]),
            )
            for row in data["scenarios"]
        )
        return _PreparedPayload(
            payload.database_json,
            payload.payload_digest,
            values,
            tools,
            scenarios,
        )

    def save(self, payload: FrozenDecisionPayload) -> str:
        prepared = self._prepare(payload)
        for attempt in range(_MAX_SAVE_ATTEMPTS):
            try:
                return self._write_transaction(prepared)
            except sqlite3.OperationalError as exc:
                message = str(exc).lower()
                if not ("locked" in message or "busy" in message):
                    raise
                if attempt + 1 == _MAX_SAVE_ATTEMPTS:
                    raise
                time.sleep(0.05 * (2**attempt))
        raise RuntimeError("Decision persistence retry loop ended unexpectedly.")

    def _write_transaction(self, prepared: _PreparedPayload) -> str:
        with closing(self._connect()) as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                existing = connection.execute(
                    "SELECT payload_digest FROM decision_records WHERE decision_id = ?",
                    (prepared.decision_values[0],),
                ).fetchone()
                if existing is not None:
                    connection.rollback()
                    return (
                        "already_saved"
                        if existing["payload_digest"] == prepared.payload_digest
                        else "idempotency_conflict"
                    )
                self._insert_decision(connection, prepared.decision_values)
                self._insert_tool_rows(connection, prepared.tool_rows)
                self._insert_scenario_rows(connection, prepared.scenario_rows)
                connection.commit()
                return "saved"
            except Exception:
                connection.rollback()
                raise

    @staticmethod
    def _insert_decision(connection: sqlite3.Connection, values: tuple[Any, ...]) -> None:
        connection.execute(
            """INSERT INTO decision_records (
                decision_id, battery_id, created_at_utc, goal_spec_json, goal_id,
                horizon_cycles, target_soh, assessment_scope,
                diagnostic_evidence_json, goal_version, config_version, result_json,
                snapshot_metadata_json, baseline_result_json, counterfactual_result_json,
                utility_ranking_json, feasibility_json, planned_tools_json,
                plan_evidence_available, executed_tools_json, final_decision_json,
                termination_status, decision_status, explanation_json,
                failure_details_json, payload_digest, record_version
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )""",
            values,
        )

    @staticmethod
    def _insert_tool_rows(
        connection: sqlite3.Connection, rows: tuple[tuple[Any, ...], ...]
    ) -> None:
        connection.executemany(
            """INSERT INTO decision_tool_outcomes (
                decision_id, tool_name, planned, executed, execution_order, status,
                validated_arguments_json, result_summary_json, error_details_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )

    @staticmethod
    def _insert_scenario_rows(
        connection: sqlite3.Connection, rows: tuple[tuple[Any, ...], ...]
    ) -> None:
        connection.executemany(
            """INSERT INTO decision_scenarios (
                decision_id, scenario_type, scenario_name, projected_soh, utility,
                feasibility_json, result_data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )

    @staticmethod
    def _summary(row: sqlite3.Row) -> dict[str, Any]:
        goal = json.loads(row["goal_spec_json"])
        return {
            "decision_id": row["decision_id"],
            "battery_id": row["battery_id"],
            "created_at": row["created_at_utc"],
            "decision_status": row["decision_status"],
            "termination_status": row["termination_status"],
            "goal_id": goal["goal_id"],
        }

    def list_decisions(
        self, battery_id: str, limit: int = 20, cursor: Optional[str] = None
    ) -> dict[str, Any]:
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("limit must be an integer between 1 and 100.")
        decoded = decode_cursor(cursor)
        query = "SELECT * FROM decision_records WHERE battery_id = ?"
        parameters: list[Any] = [battery_id]
        if decoded is not None:
            created_at, decision_id = decoded
            query += " AND (created_at_utc < ? OR (created_at_utc = ? AND decision_id < ?))"
            parameters.extend((created_at, created_at, decision_id))
        query += " ORDER BY created_at_utc DESC, decision_id DESC LIMIT ?"
        parameters.append(limit + 1)
        with closing(self._connect()) as connection:
            rows = connection.execute(query, parameters).fetchall()
        has_more = len(rows) > limit
        visible = rows[:limit]
        next_cursor = (
            encode_cursor(visible[-1]["created_at_utc"], visible[-1]["decision_id"])
            if has_more and visible
            else None
        )
        return {
            "items": [self._summary(row) for row in visible],
            "next_cursor": next_cursor,
            "has_more": has_more,
        }

    def get_decision(self, decision_id: str) -> Optional[dict[str, Any]]:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM decision_records WHERE decision_id = ?",
                (decision_id,),
            ).fetchone()
            if row is None:
                return None
            record = {
                key: row[key]
                for key in row.keys()
                if not key.endswith("_json")
            }
            for key in row.keys():
                if key.endswith("_json"):
                    record[key.removesuffix("_json")] = (
                        json.loads(row[key]) if row[key] is not None else None
                    )
            record["plan_evidence_available"] = bool(
                record["plan_evidence_available"]
            )
            tools = connection.execute(
                "SELECT * FROM decision_tool_outcomes WHERE decision_id = ? ORDER BY execution_order",
                (decision_id,),
            ).fetchall()
            scenarios = connection.execute(
                "SELECT * FROM decision_scenarios WHERE decision_id = ? ORDER BY scenario_id",
                (decision_id,),
            ).fetchall()
        record["tool_outcomes"] = []
        for tool in tools:
            record["tool_outcomes"].append(
                {
                    "outcome_id": tool["outcome_id"],
                    "tool_name": tool["tool_name"],
                    "planned": None if tool["planned"] is None else bool(tool["planned"]),
                    "executed": bool(tool["executed"]),
                    "execution_order": tool["execution_order"],
                    "status": tool["status"],
                    "validated_arguments": json.loads(tool["validated_arguments_json"])
                    if tool["validated_arguments_json"] is not None else None,
                    "result_summary": json.loads(tool["result_summary_json"])
                    if tool["result_summary_json"] is not None else None,
                    "error_details": json.loads(tool["error_details_json"])
                    if tool["error_details_json"] is not None else None,
                }
            )
        record["scenarios"] = [
            {
                "scenario_id": scenario["scenario_id"],
                "scenario_type": scenario["scenario_type"],
                "scenario_name": scenario["scenario_name"],
                "projected_soh": scenario["projected_soh"],
                "utility": scenario["utility"],
                "feasibility": json.loads(scenario["feasibility_json"])
                if scenario["feasibility_json"] is not None else None,
                "result_data": json.loads(scenario["result_data_json"]),
            }
            for scenario in scenarios
        ]
        return record
