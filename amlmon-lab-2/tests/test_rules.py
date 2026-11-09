from amlmon.config import Config
from amlmon.rules import (
    DormantAccountRule,
    HighRiskCountryRule,
    RoundAmountRule,
    StructuringRule,
    VelocityRule,
)

CFG = Config()


def test_structuring_flags_three_near_threshold_deposits(make_tx):
    txs = [make_tx(hours=h, amount=9500) for h in (0, 10, 20)]
    alerts = StructuringRule().evaluate("C1", txs, CFG)
    assert len(alerts) == 1 and alerts[0].severity == 4


def test_structuring_ignores_slow_deposits(make_tx):
    txs = [make_tx(hours=h, amount=9500) for h in (0, 60, 120)]
    assert StructuringRule().evaluate("C1", txs, CFG) == []


def test_structuring_ignores_outgoing_and_small(make_tx):
    txs = [make_tx(hours=0, amount=9500, direction="out"),
           make_tx(hours=1, amount=500),
           make_tx(hours=2, amount=9500)]
    assert StructuringRule().evaluate("C1", txs, CFG) == []


def test_velocity(make_tx):
    txs = [make_tx(hours=i * 0.5) for i in range(12)]
    alerts = VelocityRule().evaluate("C1", txs, CFG)
    assert len(alerts) == 1


def test_velocity_quiet_customer(make_tx):
    txs = [make_tx(hours=i * 5) for i in range(12)]
    assert VelocityRule().evaluate("C1", txs, CFG) == []


def test_high_risk_country(make_tx):
    txs = [make_tx(country="IR"), make_tx(country="DE")]
    alerts = HighRiskCountryRule().evaluate("C1", txs, CFG)
    assert [a.tx_ids for a in alerts] == [(txs[0].tx_id,)]


def test_round_amounts(make_tx):
    txs = [make_tx(days=d, amount=2000, direction="out") for d in (0, 2, 4)]
    assert len(RoundAmountRule().evaluate("C1", txs, CFG)) == 1


def test_round_amounts_ignores_non_round(make_tx):
    txs = [make_tx(days=d, amount=2001, direction="out") for d in (0, 2, 4)]
    assert RoundAmountRule().evaluate("C1", txs, CFG) == []


def test_dormant(make_tx):
    txs = [make_tx(days=0, amount=50), make_tx(days=200, amount=6000)]
    alerts = DormantAccountRule().evaluate("C1", txs, CFG)
    assert len(alerts) == 1 and alerts[0].tx_ids == (txs[1].tx_id,)


def test_dormant_small_amount_ok(make_tx):
    txs = [make_tx(days=0, amount=50), make_tx(days=200, amount=60)]
    assert DormantAccountRule().evaluate("C1", txs, CFG) == []
