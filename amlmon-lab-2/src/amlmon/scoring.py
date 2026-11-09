from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .config import Config
from .models import Alert


def customer_risk_scores(
    alerts: Iterable[Alert], config: Config | None = None
) -> dict[str, int]:
    """Sum severity weights per customer, capped at 100."""
    config = config or Config()
    totals: dict[str, int] = defaultdict(int)
    for a in alerts:
        totals[a.customer_id] += config.severity_weights.get(a.severity, 0)
    return {cid: min(100, score) for cid, score in totals.items()}


def risk_band(score: int) -> str:
    if score > 60:
        return "high"
    if score > 25:
        return "medium"
    return "low"
