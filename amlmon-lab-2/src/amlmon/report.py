from __future__ import annotations

import csv
import io
import json
from collections import Counter

from .config import Config
from .models import Alert
from .scoring import customer_risk_scores, risk_band


def build_summary(alerts: list[Alert], config: Config | None = None) -> dict:
    scores = customer_risk_scores(alerts, config)
    by_rule = Counter(a.rule for a in alerts)
    return {
        "total_alerts": len(alerts),
        "alerts_by_rule": dict(sorted(by_rule.items())),
        "customers": [
            {"customer_id": cid, "score": s, "band": risk_band(s)}
            for cid, s in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
    }


def to_json(summary: dict) -> str:
    return json.dumps(summary, indent=2, sort_keys=True)


def to_csv(summary: dict) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["customer_id", "score", "band"])
    for c in summary["customers"]:
        writer.writerow([c["customer_id"], c["score"], c["band"]])
    return buf.getvalue()
