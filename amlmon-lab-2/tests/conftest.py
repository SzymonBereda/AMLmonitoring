from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from amlmon.models import Transaction

BASE = datetime(2026, 3, 1, 10, 0)


@pytest.fixture
def make_tx():
    counter = {"n": 0}

    def _make(customer="C1", hours=0, amount="100", country="PL", direction="in", days=0):
        counter["n"] += 1
        return Transaction(
            tx_id=f"X{counter['n']:04d}",
            customer_id=customer,
            timestamp=BASE + timedelta(hours=hours, days=days),
            amount=Decimal(str(amount)),
            currency="EUR",
            counterparty_country=country,
            direction=direction,
        )

    return _make
