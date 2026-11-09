from __future__ import annotations

from datetime import timedelta

from ..models import Alert
from .base import Rule


class RoundAmountRule(Rule):
    """Repeated large round-number outgoing payments."""

    name = "round_amounts"

    def evaluate(self, customer_id, txs, config):
        unit = config.round_amount_unit
        rnd = [t for t in txs if t.direction == "out" and t.amount % unit == 0]
        window = timedelta(days=config.round_amount_window_days)
        alerts = []
        start = 0
        last_flagged = -1
        for end in range(len(rnd)):
            while rnd[end].timestamp - rnd[start].timestamp > window:
                start += 1
            group = rnd[start : end + 1]
            if len(group) >= config.round_amount_min_count and start > last_flagged:
                alerts.append(
                    Alert(
                        rule=self.name,
                        customer_id=customer_id,
                        severity=2,
                        tx_ids=tuple(t.tx_id for t in group),
                        message=(
                            f"{len(group)} round-amount payments within "
                            f"{config.round_amount_window_days}d"
                        ),
                        created_at=group[-1].timestamp,
                    )
                )
                last_flagged = end
        return alerts
