"""Add rule-based feature columns to the clean RFI table.

Reads data/processed/rfi_clean.csv and writes data/processed/rfi_features.csv.
The clean table is not modified.

Discipline and issue type come from the question text. A discipline written
in the question is kept. Otherwise the opening of the question is matched
to keyword rules. Document-update flags come from the notes.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "data" / "processed" / "rfi_clean.csv"
FEATURES = ROOT / "data" / "processed" / "rfi_features.csv"

FEATURE_COLUMNS = [
    "discipline",
    "issue_type",
    "drawing_update_required",
    "spec_update_required",
    "document_update_required",
    "question_word_count",
    "response_word_count",
]

STATED_DISCIPLINE = {
    "electrical": "Electrical",
    "general": "General",
    "contracting": "Other",
    "contacting": "Other",
    "civil": "Civil",
    "structural": "Structural",
    "mechanical": "Mechanical",
    "architectural": "Architectural",
    "civil / mechanical": "Mechanical",
    "quality control": "Quality / Inspection",
    "cybersecurity classification": "Cybersecurity",
    "natural gas (mechanical)": "Mechanical",
}

DISCIPLINE_RULES = [
    (
        "Other",
        [
            "buy american",
            "trade agreement",
            "davis-bacon",
            "prevailing wage",
            "liquidated damage",
            "cpars",
            "past performance",
            "far clause",
            "tax exempt",
            "tax-exempt",
            "site walk",
            "site visit",
            "bid submission",
            "notice to proceed",
            "award date",
            "funding will",
        ],
    ),
    ("Controls / SCADA", ["scada", "bas system", "ddc"]),
    ("Cybersecurity", ["cybersecurity", "rmf"]),
    ("Quality / Inspection", ["special inspection", "quality control", "field testing"]),
    ("Architectural", ["paints and coatings", "schedules for finishes"]),
    ("Mechanical", ["natural gas", "gas line"]),
    (
        "Civil",
        [
            "fence",
            "fencing",
            "chain-link",
            "chain link",
            "pavement",
            "asphalt",
            "hot-mix",
            "soil",
            "soils",
            "earthwork",
            "contaminant",
        ],
    ),
    (
        "Electrical",
        [
            "photovoltaic",
            " pv ",
            "solar",
            "battery",
            "bess",
            "transformer",
            "generator",
            "meter",
            "handhole",
            "manhole",
            "duct bank",
            "electrical",
            "grounding",
            "conduit",
            "feeder",
            "lightning",
            "impedance",
            "engine-generator",
        ],
    ),
    (
        "Structural",
        ["structural", "cast-in-place", "geotechnical", "concrete", "foundation"],
    ),
    (
        "General",
        ["temporary construction", "temporary environmental", "project schedule", "closeout"],
    ),
]

ISSUE_RULES = [
    ("Drawing Conflict", ["conflicting", "discrepancy", "conflict"]),
    (
        "Inspection / Quality",
        ["special inspection", "quality control", "qc manager", "field testing"],
    ),
    (
        "Compliance Requirement",
        [
            "davis-bacon",
            "prevailing wage",
            "buy american",
            "trade agreement",
            "ndaa",
            "far clause",
            "liquidated",
            "dpas",
            "cpars",
            "tax exempt",
            "tax-exempt",
            "cybersecurity",
            "rmf",
        ],
    ),
    (
        "Missing Information",
        [
            "please provide",
            "not included",
            "not listed",
            "not shown",
            "missing",
            "anticipated award",
            "target date",
        ],
    ),
    (
        "Interface Coordination",
        [
            "integration between",
            "integration with",
            "integration of",
            "interconnect",
            "existing scada",
            "bas system",
        ],
    ),
    (
        "Material Requirement",
        [
            "equivalent",
            "manufacturer",
            "basis-of-design",
            "basis of design",
            "material escalation",
            "racking material",
            "accept the",
        ],
    ),
    ("Scope Gap", ["scope of work", "own forces", "paid by the owner"]),
    ("Constructability", ["when constructing", "constructability"]),
]

OPENING = 240


def print_progress(done: int, total: int, label: str) -> None:
    percent = 100 if total == 0 else done * 100 // total
    print(f"\r{label}: {percent}% ({done}/{total})", end="", flush=True)


def has_term(text: str, term: str) -> bool:
    if term.startswith(" ") or term.endswith(" "):
        return term in text
    if len(term) <= 5:
        return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None
    return term in text


def first_match(text: str, rules: list[tuple[str, list[str]]]) -> str:
    for name, terms in rules:
        if any(has_term(text, term) for term in terms):
            return name
    return ""


def stated_discipline(question: str) -> str:
    match = re.search(
        r"Discipline:\s*(.+?)(?:\s+Sheet:|\s+Spec:|\s+Question:)",
        question,
        re.IGNORECASE,
    )
    if not match:
        return ""
    return STATED_DISCIPLINE.get(match.group(1).strip().lower(), "Other")


def sheet_discipline(question: str) -> str:
    if re.search(r"\b(?:ES|ED|EP|EG)\d{3}\b", question):
        return "Electrical"
    if re.search(r"\bM-\d{3}\b", question):
        return "Mechanical"
    if re.search(r"\bS-\d{3}\b", question):
        return "Structural"
    if re.search(r"\b(?:CS|CD|C)-\d{3}\b", question):
        return "Civil"
    return ""


def classify_discipline(question: str) -> str:
    stated = stated_discipline(question)
    if stated:
        return stated
    lowered = question.lower()
    opening = lowered[:OPENING]
    return (
        first_match(opening, DISCIPLINE_RULES)
        or first_match(lowered, DISCIPLINE_RULES)
        or sheet_discipline(question)
        or "Other"
    )


def is_drawing_conflict(text: str) -> bool:
    if first_match(text, ISSUE_RULES[:1]):
        return True
    return re.search(r"\bwhile\b.{0,80}\b(?:detail|sheet|drawing)", text) is not None


def is_specification(text: str) -> bool:
    return re.search(r"\bspec:|\bsection\s+\d{2}\s+\d{2}\s+\d{2}|\bsection states\b", text) is not None


def classify_issue(question: str) -> str:
    lowered = question.lower()
    for text in (lowered[:OPENING], lowered):
        if is_drawing_conflict(text):
            return "Drawing Conflict"
        matched = first_match(text, ISSUE_RULES[1:])
        if matched:
            return matched
        if re.search(r"\bmaterial\b", text[:80]):
            return "Material Requirement"
        if is_specification(text):
            return "Specification Clarification"
        if "please clarify" in text or "please confirm" in text:
            return "Design Clarification"
    if "?" in question:
        return "Design Clarification"
    return "Other"


def document_flags(notes: str) -> tuple[str, str, str]:
    text = notes.strip().lower()
    drawing = "Unknown"
    spec = "Unknown"
    if "no spec/drawing update required" in text:
        drawing, spec = "No", "No"
    elif "updated spec/dwg included" in text:
        drawing, spec = "Yes", "Yes"
    elif "updated spec included" in text:
        spec = "Yes"
    elif "drawing update provided" in text:
        drawing = "Yes"
    if drawing == "Yes" or spec == "Yes":
        document = "Yes"
    elif drawing == "No" and spec == "No":
        document = "No"
    else:
        document = "Unknown"
    return drawing, spec, document


def word_count(text: str) -> str:
    return str(len(text.split()))


def build_features(row: dict[str, str]) -> dict[str, str]:
    drawing, spec, document = document_flags(row["notes"])
    featured = dict(row)
    featured.update(
        {
            "discipline": classify_discipline(row["question"]),
            "issue_type": classify_issue(row["question"]),
            "drawing_update_required": drawing,
            "spec_update_required": spec,
            "document_update_required": document,
            "question_word_count": word_count(row["question"]),
            "response_word_count": word_count(row["response"]),
        }
    )
    return featured


def write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def print_counts(label: str, rows: list[dict[str, str]], column: str) -> None:
    print(label)
    for name, count in Counter(row[column] for row in rows).most_common():
        print(f"  {count:3} {name}")


def main() -> None:
    with CLEAN.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle))

    featured = []
    total = len(source_rows)
    for index, row in enumerate(source_rows, start=1):
        featured.append(build_features(row))
        print_progress(index, total, "Building features")
    print()

    columns = list(source_rows[0]) + FEATURE_COLUMNS
    write_csv(FEATURES, columns, featured)
    print(f"Wrote {len(featured)} rows to {FEATURES.relative_to(ROOT)}")
    print_counts("Discipline:", featured, "discipline")
    print_counts("Issue type:", featured, "issue_type")
    print_counts("Document update:", featured, "document_update_required")


if __name__ == "__main__":
    main()
