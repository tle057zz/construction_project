"""Validate the clean RFI table.

Reads data/processed/rfi_clean.csv and data/processed/rfi_excluded.csv.
Does not change either file. Writes the check results to
data/processed/validation/validation_results.csv.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "data" / "processed" / "rfi_clean.csv"
EXCLUDED = ROOT / "data" / "processed" / "rfi_excluded.csv"
RESULTS = ROOT / "data" / "processed" / "validation" / "validation_results.csv"

EXPECTED_COLUMNS = [
    "rfi_id",
    "from_party",
    "tasked_to",
    "date_received",
    "question",
    "response",
    "notes",
    "status",
    "response_available",
]
EXPECTED_COUNT = 107


def print_progress(done: int, total: int, label: str) -> None:
    percent = 100 if total == 0 else done * 100 // total
    print(f"\r{label}: {percent}% ({done}/{total})", end="", flush=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def expected_ids() -> list[str]:
    return [f"RFI-{number:03d}" for number in range(1, EXPECTED_COUNT + 1)]


def is_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def record(name: str, passed: bool, detail: str) -> dict[str, str]:
    return {
        "check": name,
        "result": "PASS" if passed else "FAIL",
        "detail": detail,
    }


def validate(rows: list[dict[str, str]], excluded: list[dict[str, str]]) -> list[dict[str, str]]:
    checks = []
    columns = list(rows[0]) if rows else []
    checks.append(
        record(
            "columns",
            columns == EXPECTED_COLUMNS,
            ", ".join(columns),
        )
    )
    checks.append(
        record(
            "row_count",
            len(rows) == EXPECTED_COUNT,
            f"{len(rows)} rows",
        )
    )

    ids = [row["rfi_id"] for row in rows]
    checks.append(
        record(
            "rfi_id_sequence",
            ids == expected_ids(),
            f"{ids[0]} to {ids[-1]}" if ids else "no rows",
        )
    )

    missing_question = []
    missing_party = []
    missing_tasked = []
    bad_dates = []
    status_mismatches = []
    total = len(rows)
    for index, row in enumerate(rows, start=1):
        if not row["question"].strip():
            missing_question.append(row["rfi_id"])
        if not row["from_party"].strip():
            missing_party.append(row["rfi_id"])
        if not row["tasked_to"].strip():
            missing_tasked.append(row["rfi_id"])
        if not is_iso_date(row["date_received"]):
            bad_dates.append(row["rfi_id"])
        answered = row["status"] == "Answered" and row["response_available"] == "Yes" and bool(row["response"].strip())
        open_row = row["status"] == "Open" and row["response_available"] == "No" and not row["response"].strip()
        if not answered and not open_row:
            status_mismatches.append(row["rfi_id"])
        print_progress(index, total, "Checking rows")
    print()

    checks.append(record("question_present", not missing_question, f"{len(missing_question)} blank"))
    checks.append(record("from_party_present", not missing_party, f"{len(missing_party)} blank"))
    checks.append(record("tasked_to_present", not missing_tasked, f"{len(missing_tasked)} blank"))
    checks.append(record("date_received_iso", not bad_dates, f"{len(bad_dates)} invalid"))
    checks.append(
        record(
            "status_matches_response",
            not status_mismatches,
            f"{len(status_mismatches)} mismatches",
        )
    )

    clean_ids = set(ids)
    leaked = []
    for row in excluded:
        number = row["rfi_number"].strip()
        if number.isdigit() and f"RFI-{int(number):03d}" in clean_ids:
            leaked.append(number)
        elif number in clean_ids:
            leaked.append(number)
    checks.append(
        record(
            "excluded_rows_absent",
            not leaked and len(excluded) == 5,
            f"{len(excluded)} excluded, {len(leaked)} still in the clean table",
        )
    )
    return checks


def write_results(checks: list[dict[str, str]]) -> None:
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check", "result", "detail"])
        writer.writeheader()
        writer.writerows(checks)


def main() -> None:
    rows = read_csv(CLEAN)
    excluded = read_csv(EXCLUDED)
    checks = validate(rows, excluded)
    write_results(checks)
    failed = 0
    for item in checks:
        print(f"{item['result']}  {item['check']}: {item['detail']}")
        if item["result"] == "FAIL":
            failed += 1
    print(f"Wrote {RESULTS.relative_to(ROOT)}")
    if failed:
        raise SystemExit(f"{failed} check(s) failed")
    print(f"All {len(checks)} checks passed")


if __name__ == "__main__":
    main()
