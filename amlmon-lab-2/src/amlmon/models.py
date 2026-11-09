from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Transaction:
    tx_id: str
    customer_id: str
    timestamp: datetime
    amount: Decimal
    currency: str
    counterparty_country: str
    direction: str  # "in" or "out"


@dataclass(frozen=True)
class Alert:
    rule: str
    customer_id: str
    severity: int  # 1 (low) .. 5 (critical)
    tx_ids: tuple[str, ...]
    message: str
    created_at: datetime
