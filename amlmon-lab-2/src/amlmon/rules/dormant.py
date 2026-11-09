from __future__ import annotations

from datetime import timedelta

from ..models import Alert
from .base import Rule


class DormantAccountRule(Rule):
    """Large transaction after a long period of inactivity."""

    name = "dormant_account"

    def evaluate(self, customer_id, txs, config):
        gap = timedelta(days=config.dormant_days)
        alerts = []
        for prev, cur in zip(txs, txs[1:]):
            if (
                cur.timestamp - prev.timestamp >= gap
                and cur.amount >= config.dormant_min_amount
            ):
                alerts.append(
                    Alert(
                        rule=self.name,
                        customer_id=customer_id,
                        severity=3,
                        tx_ids=(cur.tx_id,),
                        message=(
                            f"{cur.amount} {cur.currency} after "
                            f"{(cur.timestamp - prev.timestamp).days} idle days"
                        ),
                        created_at=cur.timestamp,
                    )
                )
        return alerts
