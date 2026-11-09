from __future__ import annotations

from datetime import timedelta

from ..config import Config
from ..models import Alert
from .base import Rule


class StructuringRule(Rule):
    """Several deposits just under the reporting threshold in a short window."""

    name = "structuring"

    def evaluate(self, customer_id, txs, config: Config):
        floor = config.reporting_threshold * config.structuring_floor_ratio
        near = [
            t
            for t in txs
            if t.direction == "in" and floor <= t.amount < config.reporting_threshold
        ]
        window = timedelta(hours=config.structuring_window_hours)
        alerts = []
        start = 0
        last_flagged = -1
        for end in range(len(near)):
            while near[end].timestamp - near[start].timestamp > window:
                start += 1
            group = near[start : end + 1]
            if len(group) >= config.structuring_min_count and start > last_flagged:
                alerts.append(
                    Alert(
                        rule=self.name,
                        customer_id=customer_id,
                        severity=4,
                        tx_ids=tuple(t.tx_id for t in group),
                        message=(
                            f"{len(group)} deposits just below "
                            f"{config.reporting_threshold} within "
                            f"{config.structuring_window_hours}h"
                        ),
                        created_at=group[-1].timestamp,
                    )
                )
                last_flagged = end
        return alerts
