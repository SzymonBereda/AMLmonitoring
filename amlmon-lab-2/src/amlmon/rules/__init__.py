from .base import Rule
from .dormant import DormantAccountRule
from .geography import HighRiskCountryRule
from .round_amounts import RoundAmountRule
from .structuring import StructuringRule
from .velocity import VelocityRule


def default_rules() -> list[Rule]:
    return [
        StructuringRule(),
        VelocityRule(),
        HighRiskCountryRule(),
        RoundAmountRule(),
        DormantAccountRule(),
    ]


__all__ = [
    "Rule",
    "default_rules",
    "StructuringRule",
    "VelocityRule",
    "HighRiskCountryRule",
    "RoundAmountRule",
    "DormantAccountRule",
]
