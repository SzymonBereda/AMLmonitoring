from __future__ import annotations

import argparse
import sys

from . import cases, report, store
from .config import Config
from .engine import run_rules
from .ingest import IngestError, read_transactions


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="amlmon")
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="ingest a CSV and store alerts")
    run.add_argument("--input", required=True)
    run.add_argument("--db", required=True)
    run.add_argument("--config")

    rep = sub.add_parser("report", help="print a summary of stored alerts")
    rep.add_argument("--db", required=True)
    rep.add_argument("--format", choices=["json", "csv"], default="json")

    case = sub.add_parser("case", help="case management")
    csub = case.add_subparsers(dest="case_command", required=True)
    op = csub.add_parser("open")
    op.add_argument("--db", required=True)
    op.add_argument("--alert-ids", type=int, nargs="+", required=True)
    adv = csub.add_parser("advance")
    adv.add_argument("--db", required=True)
    adv.add_argument("--case-id", type=int, required=True)
    adv.add_argument("--to", required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "run":
            config = Config.load(args.config) if args.config else Config()
            txs, errors = read_transactions(args.input)
            for e in errors:
                print(f"warning: {e}", file=sys.stderr)
            alerts = run_rules(txs, config)
            conn = store.connect(args.db)
            new = store.save_alerts(conn, alerts)
            print(f"{len(txs)} transactions, {len(alerts)} alerts ({new} new)")
        elif args.command == "report":
            conn = store.connect(args.db)
            alerts = [a for _, a in store.list_alerts(conn)]
            summary = report.build_summary(alerts)
            out = report.to_json(summary) if args.format == "json" else report.to_csv(summary)
            print(out)
        elif args.command == "case":
            conn = store.connect(args.db)
            if args.case_command == "open":
                print(cases.open_case(conn, args.alert_ids))
            else:
                cases.advance_case(conn, args.case_id, args.to)
                print(f"case {args.case_id} -> {args.to}")
    except (IngestError, cases.CaseError, cases.InvalidTransition, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
