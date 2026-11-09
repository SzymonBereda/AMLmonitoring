from __future__ import annotations

from datetime import timedelta

from ..models import Alert
from .base import Rule


class VelocityRule(Rule):
    """Unusually many transactions in a short window."""

    name = "velocity"

    def evaluate(self, customer_id, txs, config):
        window = timedelta(hours=config.velocity_window_hours)
        alerts = []
        start = 0
        flagged_until = -1
        for end in range(len(txs)):
            while txs[end].timestamp - txs[start].timestamp > window:
                start += 1
            count = end - start + 1
            if count > config.velocity_max_tx and start > flagged_until:
                group = txs[start : end + 1]
                alerts.append(
                    Alert(
                        rule=self.name,
                        customer_id=customer_id,
                        severity=2,
                        tx_ids=tuple(t.tx_id for t in group),
                        message=(
                            f"{count} transactions within "
                            f"{config.velocity_window_hours}h"
                        ),
                        created_at=txs[end].timestamp,
                    )
                )
                flagged_until = end
        return alerts
