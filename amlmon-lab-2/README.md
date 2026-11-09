# amlmon

A small, dependency-free, rule-based AML transaction monitoring toolkit.

Pipeline: CSV ingest -> rules engine -> alerts (SQLite) -> case workflow -> reports.

```
python -m amlmon.cli run --input data/sample_transactions.csv --db alerts.db
python -m amlmon.cli report --db alerts.db --format json
python -m amlmon.cli case open --db alerts.db --alert-ids 1 2
python -m amlmon.cli case advance --db alerts.db --case-id 1 --to investigating
```

Run tests: `pip install pytest && pytest`.

Rules live in `src/amlmon/rules/`; thresholds in `config.py`.

## Intended behaviour

- Risk bands: score 60 and above is `high`, 25 and above is `medium`, otherwise `low`.
- An alert may belong to at most one case that is not yet `closed`.
- `amlmon report` uses the same configuration as the `run` that produced the alerts.
- Timestamps may carry a UTC offset or not; a CSV may contain both and must still be processed.
- All monetary thresholds are expressed in EUR. Transactions in other currencies
  must be compared on an EUR basis (use the rates file when available).
- Customer ids come from untrusted CSV files.
