import pytest

from amlmon import cases, store
from amlmon.engine import run_rules


@pytest.fixture
def conn(tmp_path, make_tx):
    c = store.connect(tmp_path / "a.db")
    alerts = run_rules([make_tx(country="IR"), make_tx(country="SY", hours=1)])
    store.save_alerts(c, alerts)
    return c


def test_save_alerts_is_idempotent(conn, make_tx):
    alerts = [a for _, a in store.list_alerts(conn)]
    assert store.save_alerts(conn, alerts) == 0
    assert len(store.list_alerts(conn)) == 2


def test_case_lifecycle(conn):
    cid = cases.open_case(conn, [1, 2])
    cases.advance_case(conn, cid, "investigating")
    cases.advance_case(conn, cid, "escalated")
    cases.advance_case(conn, cid, "closed")
    assert [e["to_status"] for e in cases.case_history(conn, cid)] == [
        "open", "investigating", "escalated", "closed"]


def test_invalid_transition(conn):
    cid = cases.open_case(conn, [1])
    with pytest.raises(cases.InvalidTransition):
        cases.advance_case(conn, cid, "escalated")


def test_closed_is_terminal(conn):
    cid = cases.open_case(conn, [1])
    cases.advance_case(conn, cid, "closed")
    with pytest.raises(cases.InvalidTransition):
        cases.advance_case(conn, cid, "open")


def test_open_case_unknown_alert(conn):
    with pytest.raises(cases.CaseError):
        cases.open_case(conn, [999])
