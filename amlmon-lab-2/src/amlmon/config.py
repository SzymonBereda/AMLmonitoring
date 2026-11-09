from __future__ import annotations

import json
from dataclasses import dataclass, field, fields
from decimal import Decimal
from pathlib import Path


@dataclass
class Config:
    reporting_threshold: Decimal = Decimal("10000")
    structuring_floor_ratio: Decimal = Decimal("0.80")
    structuring_window_hours: int = 48
    structuring_min_count: int = 3
    velocity_max_tx: int = 10
    velocity_window_hours: int = 24
    high_risk_countries: tuple[str, ...] = ("IR", "KP", "MM", "SY")
    round_amount_unit: Decimal = Decimal("1000")
    round_amount_min_count: int = 3
    round_amount_window_days: int = 7
    dormant_days: int = 180
    dormant_min_amount: Decimal = Decimal("5000")
    severity_weights: dict = field(
        default_factory=lambda: {1: 2, 2: 5, 3: 10, 4: 20, 5: 40}
    )

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        known = {f.name for f in fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"unknown config keys: {sorted(unknown)}")
        kwargs = dict(data)
        for key in (
            "reporting_threshold",
            "structuring_floor_ratio",
            "round_amount_unit",
            "dormant_min_amount",
        ):
            if key in kwargs:
                kwargs[key] = Decimal(str(kwargs[key]))
        if "high_risk_countries" in kwargs:
            kwargs["high_risk_countries"] = tuple(kwargs["high_risk_countries"])
        if "severity_weights" in kwargs:
            kwargs["severity_weights"] = {
                int(k): v for k, v in kwargs["severity_weights"].items()
            }
        return cls(**kwargs)

    @classmethod
    def load(cls, path: str | Path) -> "Config":
        return cls.from_dict(json.loads(Path(path).read_text()))
