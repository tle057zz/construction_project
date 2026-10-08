"""Clean the raw RFI table into an analytical table.

Reads data/processed/raw_rfi.csv and writes data/processed/rfi_clean.csv.
The workbook and the raw table are not modified.

Rows that are not RFI records are written to
data/processed/rfi_excluded.csv.
"""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "processed" / "raw_rfi.csv"
CLEAN = ROOT / "data" / "processed" / "rfi_clean.csv"
EXCLUDED = ROOT / "data" / "processed" / "rfi_excluded.csv"

EXCEL_EPOCH = date(1899, 12, 30)

CLEAN_COLUMNS = [
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


def print_progress(done: int, total: int, label: str) -> None:
    percent = 100 if total == 0 else done * 100 // total
    print(f"\r{label}: {percent}% ({done}/{total})", end="", flush=True)


def clean_text(value: str) -> str:
    text = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    lines = [" ".join(line.split()) for line in text.split("\n")]
    return "\n".join(line for line in lines if line)


def excel_serial_to_date(value: str) -> str:
    serial = int(value)
    return (EXCEL_EPOCH + timedelta(days=serial)).isoformat()


def rfi_id(value: str) -> str:
    return f"RFI-{int(value):03d}"


def exclusion_reason(row: dict[str, str]) -> str:
    number = row["rfi_number"].strip()
    if not number.isdigit():
        return "section label, not an RFI record"
    if not any(row[field].strip() for field in ("from_party", "date_received", "question")):
        return "identifier only, no party, date, or question"
    return ""


def clean_row(row: dict[str, str]) -> dict[str, str]:
    response = clean_text(row["response"])
    source_status = clean_text(row["status_raw"])
    answered = bool(response)
    return {
        "rfi_id": rfi_id(row["rfi_number"]),
        "from_party": clean_text(row["from_party"]),
        "tasked_to": clean_text(row["tasked_to"]),
        "date_received": excel_serial_to_date(row["date_received"]),
        "question": clean_text(row["question"]),
        "response": response,
        "notes": clean_text(row["notes"]),
        "status": source_status if source_status else ("Answered" if answered else "Open"),
        "response_available": "Yes" if answered else "No",
    }


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with RAW.open(encoding="utf-8", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))

    cleaned = []
    excluded = []
    total = len(raw_rows)
    for index, row in enumerate(raw_rows, start=1):
        reason = exclusion_reason(row)
        if reason:
            excluded.append({"rfi_number": row["rfi_number"].strip(), "reason": reason})
        else:
            cleaned.append(clean_row(row))
        print_progress(index, total, "Cleaning RFIs")
    print()

    write_csv(CLEAN, CLEAN_COLUMNS, cleaned)
    write_csv(EXCLUDED, ["rfi_number", "reason"], excluded)

    answered = sum(row["status"] == "Answered" for row in cleaned)
    print(f"Kept {len(cleaned)} rows in {CLEAN.relative_to(ROOT)}")
    print(f"Excluded {len(excluded)} rows in {EXCLUDED.relative_to(ROOT)}")
    print(f"Answered: {answered}")
    print(f"Open: {len(cleaned) - answered}")


if __name__ == "__main__":
    main()
