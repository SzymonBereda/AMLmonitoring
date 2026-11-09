import pytest

from amlmon.ingest import IngestError, read_transactions

HEADER = "tx_id,customer_id,timestamp,amount,currency,counterparty_country,direction\n"


def write(tmp_path, body, header=HEADER):
    p = tmp_path / "t.csv"
    p.write_text(header + body)
    return p


def test_reads_valid_rows(tmp_path):
    p = write(tmp_path, "A1,C1,2026-01-01T10:00:00,150.50,eur,pl,IN\n")
    txs, errors = read_transactions(p)
    assert errors == []
    assert txs[0].currency == "EUR" and txs[0].direction == "in"


def test_skips_bad_rows_and_reports(tmp_path):
    body = (
        "A1,C1,2026-01-01T10:00:00,150,EUR,PL,in\n"
        "A2,C1,not-a-date,150,EUR,PL,in\n"
        "A3,C1,2026-01-01T10:00:00,-5,EUR,PL,in\n"
        "A1,C1,2026-01-02T10:00:00,150,EUR,PL,in\n"
    )
    txs, errors = read_transactions(write(tmp_path, body))
    assert len(txs) == 1
    assert len(errors) == 3
    assert any("duplicate" in e for e in errors)


def test_missing_columns_raise(tmp_path):
    with pytest.raises(IngestError):
        read_transactions(write(tmp_path, "", header="tx_id,customer_id\n"))
