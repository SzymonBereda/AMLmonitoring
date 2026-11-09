from __future__ import annotations

from ..models import Alert
from .base import Rule


class HighRiskCountryRule(Rule):
    name = "high_risk_country"

    def evaluate(self, customer_id, txs, config):
        return [
            Alert(
                rule=self.name,
                customer_id=customer_id,
                severity=3,
                tx_ids=(t.tx_id,),
                message=f"counterparty in high-risk country {t.counterparty_country}",
                created_at=t.timestamp,
            )
            for t in txs
            if t.counterparty_country in config.high_risk_countries
        ]
