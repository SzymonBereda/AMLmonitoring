from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import Alert

SCHEMA = """
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    severity INTEGER NOT NULL,
    tx_ids TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (rule, customer_id, tx_ids)
);
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL,
    opened_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS case_alerts (
    case_id INTEGER NOT NULL REFERENCES cases(id),
    alert_id INTEGER NOT NULL REFERENCES alerts(id),
    PRIMARY KEY (case_id, alert_id)
);
CREATE TABLE IF NOT EXISTS case_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL REFERENCES cases(id),
    from_status TEXT,
    to_status TEXT NOT NULL,
    at TEXT NOT NULL
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def save_alerts(conn: sqlite3.Connection, alerts: Iterable[Alert]) -> int:
    """Insert alerts, ignoring ones already stored. Returns number inserted."""
    inserted = 0
    for a in alerts:
        cur = conn.execute(
            "INSERT OR IGNORE INTO alerts "
            "(rule, customer_id, severity, tx_ids, message, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                a.rule,
                a.customer_id,
                a.severity,
                json.dumps(list(a.tx_ids)),
                a.message,
                a.created_at.isoformat(),
            ),
        )
        inserted += cur.rowcount
    conn.commit()
    return inserted


def _row_to_alert(row: sqlite3.Row) -> Alert:
    return Alert(
        rule=row["rule"],
        customer_id=row["customer_id"],
        severity=row["severity"],
        tx_ids=tuple(json.loads(row["tx_ids"])),
        message=row["message"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def list_alerts(conn: sqlite3.Connection, customer_id: str | None = None):
    sql = "SELECT * FROM alerts"
    if customer_id:
        sql += f" WHERE customer_id = '{customer_id}'"
    sql += " ORDER BY created_at, id"
    return [(r["id"], _row_to_alert(r)) for r in conn.execute(sql)]
