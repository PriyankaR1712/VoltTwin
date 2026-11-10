"""Isolated SQLite state for adaptive observation evaluations."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import uuid
from contextlib import closing
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
_PROCESS_LEASES: dict[str, dict[str, Any]] = {}
_PROCESS_LEASES_LOCK = threading.Lock()


def _acquire_process_lease(database_path: Path) -> tuple[str, bool]:
    """Hold one OS lock per database so only one worker owns recovery/execution."""
    key = os.path.normcase(str(database_path.resolve()))
    with _PROCESS_LEASES_LOCK:
        existing = _PROCESS_LEASES.get(key)
        if existing is not None:
            if existing["pid"] != os.getpid():
                raise RuntimeError("Adaptive evaluation database lease was inherited across a worker fork.")
            existing["references"] += 1
            return key, False
        lock_path = database_path.with_suffix(database_path.suffix + ".worker.lock")
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        handle = open(lock_path, "a+b")
        try:
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, BlockingIOError) as exc:
            handle.close()
            raise RuntimeError("Adaptive evaluation database is already owned by another worker.") from exc
        _PROCESS_LEASES[key] = {"handle": handle, "references": 1, "pid": os.getpid()}
        return key, True


def _release_process_lease(key: str) -> None:
    with _PROCESS_LEASES_LOCK:
        lease = _PROCESS_LEASES.get(key)
        if lease is None:
            return
        lease["references"] -= 1
        if lease["references"]:
            return
        handle = lease["handle"]
        try:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()
            del _PROCESS_LEASES[key]


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


class AdaptiveEvaluationStore:
    """Persist event receipts and evaluation watermarks independently of Stage 4."""

    def __init__(self, database_path: str | Path | None = None):
        self.database_path = Path(database_path) if database_path else (
            Path(__file__).resolve().parents[1] / "data" / "adaptive_evaluation.db"
        )
        self._lease_key, is_process_owner = _acquire_process_lease(self.database_path)
        self._closed = False
        try:
            self.initialize_schema()
            if is_process_owner:
                self.recover_abandoned_events()
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            _release_process_lease(self._lease_key)

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def _connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path, timeout=0.1)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize_schema(self) -> None:
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, SCHEMA_VERSION):
                raise RuntimeError("Unsupported adaptive evaluation schema version")
            db.execute(
                """CREATE TABLE IF NOT EXISTS adaptive_evaluation_events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    evaluation_id TEXT NOT NULL UNIQUE,
                    event_key TEXT NOT NULL UNIQUE,
                    battery_id TEXT NOT NULL,
                    generation_id TEXT NOT NULL,
                    goal_fingerprint TEXT NOT NULL,
                    goal_spec_json TEXT NOT NULL,
                    event_watermark_json TEXT NOT NULL,
                    decision_snapshot_watermark_json TEXT,
                    predicted_soh REAL,
                    status TEXT NOT NULL CHECK(status IN (
                        'in_progress','held','reassessed','not_ready','stale_event',
                        'failed','indeterminate'
                    )),
                    trigger_reasons_json TEXT NOT NULL,
                    latched_side TEXT,
                    minimum_gap INTEGER NOT NULL,
                    epsilon_soh REAL NOT NULL,
                    policy_version TEXT NOT NULL,
                    prior_decision_id TEXT,
                    decision_id TEXT,
                    stage4_persistence_status TEXT,
                    created_at_utc TEXT NOT NULL DEFAULT
                        (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                )"""
            )
            db.execute("CREATE INDEX IF NOT EXISTS idx_adaptive_events_latest ON adaptive_evaluation_events(battery_id, generation_id, sequence DESC)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_adaptive_events_decision ON adaptive_evaluation_events(decision_id)")
            db.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            # Recovery is explicit; opening another store instance must not
            # invalidate a decision that may still be running.
            db.commit()

    def recover_abandoned_events(self) -> int:
        """Mark reservations left by the prior lock owner indeterminate."""
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            cursor = db.execute(
                "UPDATE adaptive_evaluation_events SET status='indeterminate' WHERE status='in_progress'"
            )
            db.commit()
            return cursor.rowcount

    def reserve(self, *, event_key: str, battery_id: str, generation_id: str,
                goal_fingerprint: str, goal_spec: dict, event_watermark: dict,
                predicted_soh: float | None, minimum_gap: int, epsilon_soh: float,
                policy_version: str, prior_decision_id: str | None) -> tuple[str, dict | None]:
        with closing(self._connect()) as db:
            try:
                db.execute("BEGIN IMMEDIATE")
                prior = db.execute("SELECT * FROM adaptive_evaluation_events WHERE event_key=?", (event_key,)).fetchone()
                if prior is not None:
                    db.commit()
                    return "existing", dict(prior)
                evaluation_id = str(uuid.uuid4())
                db.execute(
                    """INSERT INTO adaptive_evaluation_events
                    (evaluation_id,event_key,battery_id,generation_id,goal_fingerprint,goal_spec_json,
                    event_watermark_json,predicted_soh,status,trigger_reasons_json,minimum_gap,
                    epsilon_soh,policy_version,prior_decision_id)
                    VALUES (?,?,?,?,?,?,?,?, 'in_progress','[]',?,?,?,?)""",
                    (evaluation_id,event_key,battery_id,generation_id,goal_fingerprint,_json(goal_spec),
                     _json(event_watermark),predicted_soh,minimum_gap,epsilon_soh,policy_version,prior_decision_id),
                )
                db.commit()
                return evaluation_id, None
            except Exception:
                db.rollback()
                raise

    def finish(self, evaluation_id: str, *, status: str, reasons: list[str],
               latched_side: str | None = None, decision_id: str | None = None,
               persistence_status: str | None = None,
               decision_snapshot_watermark: dict | None = None) -> None:
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            cursor = db.execute(
                """UPDATE adaptive_evaluation_events SET status=?,trigger_reasons_json=?,
                latched_side=?,decision_id=?,stage4_persistence_status=?,
                decision_snapshot_watermark_json=? WHERE evaluation_id=? AND status='in_progress'""",
                (status,_json(reasons),latched_side,decision_id,persistence_status,
                 None if decision_snapshot_watermark is None else _json(decision_snapshot_watermark),evaluation_id),
            )
            if cursor.rowcount != 1:
                db.rollback()
                raise RuntimeError("Evaluation reservation is no longer in progress")
            db.commit()

    def get_latest(self, battery_id: str, generation_id: str) -> dict | None:
        with closing(self._connect()) as db:
            row = db.execute(
                """SELECT * FROM adaptive_evaluation_events WHERE battery_id=? AND generation_id=?
                AND status IN ('held','reassessed','not_ready')
                ORDER BY sequence DESC LIMIT 1""",
                (battery_id,generation_id),
            ).fetchone()
        return self._decode(dict(row)) if row else None

    def get_latest_decision_id(self, battery_id: str, generation_id: str) -> str | None:
        """Return the latest decision from a completed reassessment event."""
        with closing(self._connect()) as db:
            row = db.execute(
                """SELECT decision_id FROM adaptive_evaluation_events
                WHERE battery_id=? AND generation_id=? AND status='reassessed'
                AND decision_id IS NOT NULL ORDER BY sequence DESC LIMIT 1""",
                (battery_id,generation_id),
            ).fetchone()
        return row["decision_id"] if row else None

    def get_event(self, event_key: str) -> dict | None:
        with closing(self._connect()) as db:
            row = db.execute("SELECT * FROM adaptive_evaluation_events WHERE event_key=?", (event_key,)).fetchone()
        return self._decode(dict(row)) if row else None

    def mark_indeterminate(self, event_key: str) -> None:
        """Close an abandoned reservation without retrying its decision call."""
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "UPDATE adaptive_evaluation_events SET status='indeterminate' WHERE event_key=? AND status='in_progress'",
                (event_key,),
            )
            db.commit()

    def find_unresolved(self, battery_id: str, goal_fingerprint: str,
                        event_watermark: dict) -> dict | None:
        """Find an unresolved matching observation even after generation reset."""
        with closing(self._connect()) as db:
            row = db.execute(
                """SELECT * FROM adaptive_evaluation_events
                WHERE battery_id=? AND goal_fingerprint=? AND event_watermark_json=?
                AND status IN ('in_progress','indeterminate')
                ORDER BY sequence DESC LIMIT 1""",
                (battery_id, goal_fingerprint, _json(event_watermark)),
            ).fetchone()
        return self._decode(dict(row)) if row else None

    @staticmethod
    def _decode(row: dict) -> dict:
        for column in ("goal_spec_json", "event_watermark_json", "decision_snapshot_watermark_json", "trigger_reasons_json"):
            row[column.removesuffix("_json")] = None if row[column] is None else json.loads(row[column])
        return row
