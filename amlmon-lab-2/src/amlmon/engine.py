from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .config import Config
from .models import Alert, Transaction
from .rules import Rule, default_rules


def group_by_customer(txs: Iterable[Transaction]) -> dict[str, list[Transaction]]:
    grouped: dict[str, list[Transaction]] = defaultdict(list)
    for t in txs:
        grouped[t.customer_id].append(t)
    for lst in grouped.values():
        lst.sort(key=lambda t: (t.timestamp, t.tx_id))
    return grouped


def run_rules(
    txs: Iterable[Transaction],
    config: Config | None = None,
    rules: list[Rule] | None = None,
) -> list[Alert]:
    config = config or Config()
    rules = rules if rules is not None else default_rules()
    alerts: list[Alert] = []
    seen: set[tuple] = set()
    for customer_id, customer_txs in sorted(group_by_customer(txs).items()):
        for rule in rules:
            for alert in rule.evaluate(customer_id, customer_txs, config):
                key = (alert.rule, alert.customer_id, alert.tx_ids)
                if key in seen:
                    continue
                seen.add(key)
                alerts.append(alert)
    alerts.sort(key=lambda a: (a.created_at, a.customer_id, a.rule))
    return alerts
