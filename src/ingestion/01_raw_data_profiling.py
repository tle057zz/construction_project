"""Profile the raw USACE RFI workbook.

Opens data/raw/rfi_log.xlsx, finds the real header row, and writes
docs/data_profiling.md. The workbook is not modified.
"""

from __future__ import annotations

import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
WORKBOOK = ROOT / "data" / "raw" / "rfi_log.xlsx"
SUMMARY = ROOT / "docs" / "data_profiling.md"

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

COLUMN_MAP = {
    "RFI #": "rfi_number",
    "FROM": "from_party",
    "TASKED": "tasked_to",
    "DATE RECEIVED": "date_received",
    "QUESTION": "question",
    "RESPONSE": "response",
    "NOTES": "notes",
    "Status": "status_raw",
}


def column_index(cell_ref: str) -> int:
    letters = "".join(char for char in cell_ref if char.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + ord(char.upper()) - 64
    return index - 1


def shared_strings(workbook: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in workbook.namelist():
        return []
    root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
    values = []
    for item in root.findall("m:si", NS):
        values.append("".join(node.text or "" for node in item.findall(".//m:t", NS)))
    return values


def cell_text(cell: ET.Element, strings: list[str]) -> str:
    cell_type = cell.get("t")
    value = cell.find("m:v", NS)
    if value is None or value.text is None:
        inline = cell.find("m:is", NS)
        if inline is None:
            return ""
        return "".join(node.text or "" for node in inline.findall(".//m:t", NS))
    if cell_type == "s":
        return strings[int(value.text)]
    return value.text


def sheet_rows(path: Path) -> list[list[str]]:
    with zipfile.ZipFile(path) as workbook:
        strings = shared_strings(workbook)
        root = ET.fromstring(workbook.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in root.findall("m:sheetData/m:row", NS):
        cells = {}
        width = 0
        for cell in row.findall("m:c", NS):
            index = column_index(cell.get("r", "A1"))
            cells[index] = cell_text(cell, strings).strip()
            width = max(width, index + 1)
        rows.append([cells.get(index, "") for index in range(width)])
    return rows


def find_header_row(rows: list[list[str]]) -> int:
    for index, row in enumerate(rows):
        if any(value == "RFI #" for value in row):
            return index
    raise ValueError("Header row containing 'RFI #' was not found.")


def standardise(rows: list[list[str]], header_index: int) -> list[dict[str, str]]:
    header = rows[header_index]
    names = [COLUMN_MAP.get(name, name.strip().lower().replace(" ", "_")) for name in header]
    records = []
    for row in rows[header_index + 1 :]:
        padded = row + [""] * (len(names) - len(row))
        record = {names[index]: padded[index].strip() for index in range(len(names)) if names[index]}
        if record.get("rfi_number"):
            records.append(record)
    return records


def blank_count(records: list[dict[str, str]], field: str) -> int:
    return sum(not record.get(field) for record in records)


def lengths(records: list[dict[str, str]], field: str) -> list[int]:
    return [len(record.get(field, "")) for record in records if record.get(field)]


def median(values: list[int]) -> int:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) // 2


def value_counts(records: list[dict[str, str]], field: str) -> list[tuple[str, int]]:
    counts = Counter(record.get(field) or "(blank)" for record in records)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def bullet_list(pairs: list[tuple[str, int]]) -> str:
    return "\n".join(f"- {name}: {count}" for name, count in pairs)


def build_summary(rows: list[list[str]], header_index: int, records: list[dict[str, str]]) -> str:
    question_lengths = lengths(records, "question")
    response_lengths = lengths(records, "response")
    total = len(records)
    responses_present = total - blank_count(records, "response")
    id_counts = Counter(record["rfi_number"] for record in records)
    duplicates = sorted(rfi_id for rfi_id, count in id_counts.items() if count > 1)
    date_values = [record["date_received"] for record in records if record.get("date_received")]
    numeric_dates = sum(value.isdigit() for value in date_values)

    lines = [
        "# Raw RFI data profile",
        "",
        "Source file: `data/raw/rfi_log.xlsx`",
        "",
        "The workbook was read only. No values were changed.",
        "",
        "## Workbook shape",
        "",
        f"- Sheet rows read: {len(rows)}",
        f"- Header row: Excel row {header_index + 1}",
        f"- Title rows above the header: {header_index}",
        f"- RFI records: {total}",
        f"- Columns: {', '.join(COLUMN_MAP)}",
        "",
        "The rows above the header are title rows, not RFI records.",
        "",
        "## Missing values",
        "",
        f"- rfi_number: {blank_count(records, 'rfi_number')}",
        f"- from_party: {blank_count(records, 'from_party')}",
        f"- tasked_to: {blank_count(records, 'tasked_to')}",
        f"- date_received: {blank_count(records, 'date_received')}",
        f"- question: {blank_count(records, 'question')}",
        f"- response: {blank_count(records, 'response')}",
        f"- notes: {blank_count(records, 'notes')}",
        f"- status_raw: {blank_count(records, 'status_raw')}",
        "",
        "## Duplicate RFI IDs",
        "",
    ]
    if duplicates:
        lines.append("Duplicate RFI numbers: " + ", ".join(duplicates))
    else:
        lines.append(f"No duplicate RFI numbers in {total} records.")

    lines.extend(
        [
            "",
            "## Dates",
            "",
            f"- Populated date_received values: {len(date_values)}",
            f"- Values stored as Excel serial numbers: {numeric_dates}",
            "",
            "## Question length",
            "",
            f"- Questions with text: {len(question_lengths)}",
            f"- Shortest question: {min(question_lengths)} characters",
            f"- Median question: {median(question_lengths)} characters",
            f"- Longest question: {max(question_lengths)} characters",
            "",
            "## Response completeness",
            "",
            f"- Responses with text: {responses_present} of {total}",
            f"- Blank responses: {blank_count(records, 'response')}",
            f"- Shortest response: {min(response_lengths)} characters",
            f"- Median response: {median(response_lengths)} characters",
            f"- Longest response: {max(response_lengths)} characters",
            "",
            "## Notes",
            "",
            f"- Notes with text: {total - blank_count(records, 'notes')}",
            f"- Blank notes: {blank_count(records, 'notes')}",
            "",
            "## Status",
            "",
            bullet_list(value_counts(records, "status_raw")),
            "",
            "## FROM",
            "",
            bullet_list(value_counts(records, "from_party")),
            "",
            "## TASKED",
            "",
            bullet_list(value_counts(records, "tasked_to")),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    rows = sheet_rows(WORKBOOK)
    header_index = find_header_row(rows)
    records = standardise(rows, header_index)
    summary = build_summary(rows, header_index, records)
    SUMMARY.write_text(summary, encoding="utf-8")
    print(summary)
    print(f"\nWrote {SUMMARY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
