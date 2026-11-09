from amlmon.config import Config
from amlmon.engine import run_rules
from amlmon.scoring import customer_risk_scores, risk_band


def test_engine_groups_by_customer_and_dedupes(make_tx):
    txs = [make_tx(customer="A", hours=h, amount=9500) for h in (0, 5, 10)]
    txs += [make_tx(customer="B", country="KP")]
    alerts = run_rules(txs)
    assert {a.customer_id for a in alerts} == {"A", "B"}
    assert len({(a.rule, a.customer_id, a.tx_ids) for a in alerts}) == len(alerts)


def test_engine_handles_unsorted_input(make_tx):
    txs = [make_tx(hours=h, amount=9500) for h in (20, 0, 10)]
    assert any(a.rule == "structuring" for a in run_rules(txs))


def test_scores_capped_and_banded(make_tx):
    txs = [make_tx(country="IR", hours=i) for i in range(12)]
    alerts = run_rules(txs)
    scores = customer_risk_scores(alerts, Config())
    assert scores["C1"] == 100
    assert risk_band(100) == "high" and risk_band(30) == "medium" and risk_band(3) == "low"


def test_config_rejects_unknown_keys():
    import pytest
    with pytest.raises(ValueError):
        Config.from_dict({"nope": 1})


def test_config_overrides_threshold(make_tx):
    cfg = Config.from_dict({"reporting_threshold": 5000})
    txs = [make_tx(hours=h, amount=4500) for h in (0, 5, 10)]
    assert any(a.rule == "structuring" for a in run_rules(txs, cfg))
