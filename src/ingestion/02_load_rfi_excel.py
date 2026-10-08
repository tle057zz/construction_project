"""Load the USACE RFI workbook into a raw table.

Keeps the original cell values. Dates stay as Excel serial numbers.
Does not clean, relabel, or interpret the records.
"""

from __future__ import annotations

import csv
import importlib.util
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "processed" / "raw_rfi.csv"
SOURCE_FILE = "rfi_log.xlsx"

COLUMNS = [
    "rfi_number",
    "from_party",
    "tasked_to",
    "date_received",
    "question",
    "response",
    "notes",
    "status_raw",
    "source_file",
    "ingestion_timestamp",
]


def profiling_module():
    path = Path(__file__).with_name("01_raw_data_profiling.py")
    spec = importlib.util.spec_from_file_location("raw_data_profiling", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def print_progress(current: int, total: int, width: int = 40) -> None:
    """Display a simple terminal progress bar."""
    if total == 0:
        return

    percent = current / total
    filled = int(width * percent)
    bar = "█" * filled + "-" * (width - filled)

    print(
        f"\rLoading RFI data |{bar}| "
        f"{percent * 100:6.2f}% ({current}/{total})",
        end="",
        flush=True,
    )

    if current == total:
        print()


def raw_records(module) -> list[dict[str, str]]:
    rows = module.sheet_rows(module.WORKBOOK)
    header_index = module.find_header_row(rows)
    stamped = datetime.now().replace(microsecond=0).isoformat(sep=" ")

    raw_rows = list(module.standardise(rows, header_index))
    total = len(raw_rows)

    records = []

    for index, record in enumerate(raw_rows, start=1):
        row = {
            column: record.get(column, "")
            for column in COLUMNS
            if column not in {"source_file", "ingestion_timestamp"}
        }

        row["source_file"] = SOURCE_FILE
        row["ingestion_timestamp"] = stamped
        records.append(row)

        print_progress(index, total)

    return records


def write_csv(records: list[dict[str, str]]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    print("in progress ..")
    records = raw_records(profiling_module())
    write_csv(records)

    print(
        f"Completed: wrote {len(records)} rows "
        f"to {OUTPUT.relative_to(ROOT)}"
    )


if __name__ == "__main__":

    
    main()