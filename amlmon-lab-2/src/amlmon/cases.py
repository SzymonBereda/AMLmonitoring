from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

TRANSITIONS = {
    "open": {"investigating", "closed"},
    "investigating": {"escalated", "closed"},
    "escalated": {"closed"},
    "closed": set(),
}


class InvalidTransition(Exception):
    pass


class CaseError(Exception):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def open_case(conn: sqlite3.Connection, alert_ids: list[int]) -> int:
    if not alert_ids:
        raise CaseError("a case needs at least one alert")
    placeholders = ",".join("?" * len(alert_ids))
    found = conn.execute(
        f"SELECT COUNT(*) FROM alerts WHERE id IN ({placeholders})", alert_ids
    ).fetchone()[0]
    if found != len(set(alert_ids)):
        raise CaseError("unknown alert id")
    now = _now()
    cur = conn.execute(
        "INSERT INTO cases (status, opened_at, updated_at) VALUES ('open', ?, ?)",
        (now, now),
    )
    case_id = cur.lastrowid
    for aid in set(alert_ids):
        conn.execute(
            "INSERT INTO case_alerts (case_id, alert_id) VALUES (?, ?)",
            (case_id, aid),
        )
    conn.execute(
        "INSERT INTO case_events (case_id, from_status, to_status, at) "
        "VALUES (?, NULL, 'open', ?)",
        (case_id, now),
    )
    conn.commit()
    return case_id


def advance_case(conn: sqlite3.Connection, case_id: int, to_status: str) -> None:
    row = conn.execute("SELECT status FROM cases WHERE id = ?", (case_id,)).fetchone()
    if row is None:
        raise CaseError(f"no such case {case_id}")
    current = row["status"]
    if to_status not in TRANSITIONS.get(current, set()):
        raise InvalidTransition(f"{current} -> {to_status}")
    now = _now()
    conn.execute(
        "UPDATE cases SET status = ?, updated_at = ? WHERE id = ?",
        (to_status, now, case_id),
    )
    conn.execute(
        "INSERT INTO case_events (case_id, from_status, to_status, at) "
        "VALUES (?, ?, ?, ?)",
        (case_id, current, to_status, now),
    )
    conn.commit()


def case_history(conn: sqlite3.Connection, case_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT from_status, to_status, at FROM case_events "
        "WHERE case_id = ? ORDER BY id",
        (case_id,),
    )
    return [dict(r) for r in rows]
