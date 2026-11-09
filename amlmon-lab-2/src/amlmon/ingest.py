from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .models import Transaction

REQUIRED = [
    "tx_id",
    "customer_id",
    "timestamp",
    "amount",
    "currency",
    "counterparty_country",
    "direction",
]


class IngestError(Exception):
    pass


def parse_row(row: dict, line: int) -> Transaction:
    for col in REQUIRED:
        if not (row.get(col) or "").strip():
            raise IngestError(f"line {line}: missing {col}")
    try:
        ts = datetime.fromisoformat(row["timestamp"].strip())
    except ValueError as exc:
        raise IngestError(f"line {line}: bad timestamp") from exc
    try:
        amount = Decimal(row["amount"].strip())
    except InvalidOperation as exc:
        raise IngestError(f"line {line}: bad amount") from exc
    if amount <= 0:
        raise IngestError(f"line {line}: amount must be positive")
    direction = row["direction"].strip().lower()
    if direction not in ("in", "out"):
        raise IngestError(f"line {line}: direction must be in/out")
    return Transaction(
        tx_id=row["tx_id"].strip(),
        customer_id=row["customer_id"].strip(),
        timestamp=ts,
        amount=amount,
        currency=row["currency"].strip().upper(),
        counterparty_country=row["counterparty_country"].strip().upper(),
        direction=direction,
    )


def read_transactions(path: str | Path) -> tuple[list[Transaction], list[str]]:
    """Return (transactions, errors). Bad rows are skipped and reported."""
    txs: list[Transaction] = []
    errors: list[str] = []
    seen: set[str] = set()
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise IngestError(f"missing columns: {missing}")
        for i, row in enumerate(reader, start=2):
            try:
                tx = parse_row(row, i)
            except IngestError as exc:
                errors.append(str(exc))
                continue
            if tx.tx_id in seen:
                errors.append(f"line {i}: duplicate tx_id {tx.tx_id}")
                continue
            seen.add(tx.tx_id)
            txs.append(tx)
    return txs, errors
