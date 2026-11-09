import json
from pathlib import Path

from amlmon.cli import main

SAMPLE = Path(__file__).parent.parent / "data" / "sample_transactions.csv"


def test_run_and_report(tmp_path, capsys):
    db = str(tmp_path / "x.db")
    assert main(["run", "--input", str(SAMPLE), "--db", db]) == 0
    capsys.readouterr()
    assert main(["report", "--db", db, "--format", "json"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["total_alerts"] > 0
    assert "structuring" in summary["alerts_by_rule"]


def test_rerun_adds_no_duplicates(tmp_path, capsys):
    db = str(tmp_path / "x.db")
    main(["run", "--input", str(SAMPLE), "--db", db])
    capsys.readouterr()
    main(["run", "--input", str(SAMPLE), "--db", db])
    assert "(0 new)" in capsys.readouterr().out


def test_csv_report(tmp_path, capsys):
    db = str(tmp_path / "x.db")
    main(["run", "--input", str(SAMPLE), "--db", db])
    capsys.readouterr()
    main(["report", "--db", db, "--format", "csv"])
    assert capsys.readouterr().out.startswith("customer_id,score,band")


def test_case_commands(tmp_path, capsys):
    db = str(tmp_path / "x.db")
    main(["run", "--input", str(SAMPLE), "--db", db])
    capsys.readouterr()
    assert main(["case", "open", "--db", db, "--alert-ids", "1"]) == 0
    assert main(["case", "advance", "--db", db, "--case-id", "1", "--to", "escalated"]) == 1
