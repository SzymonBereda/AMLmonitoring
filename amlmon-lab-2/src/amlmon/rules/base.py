from __future__ import annotations

from abc import ABC, abstractmethod

from ..config import Config
from ..models import Alert, Transaction


class Rule(ABC):
    name: str = "base"

    @abstractmethod
    def evaluate(
        self, customer_id: str, txs: list[Transaction], config: Config
    ) -> list[Alert]:
        """txs are sorted by timestamp and belong to one customer."""
