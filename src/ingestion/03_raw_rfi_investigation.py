"""Investigate the loaded USACE RFI raw table.

This script does not clean or transform the data.
It only investigates structure, completeness, uniqueness,
duplicate records, categorical values, and text lengths.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "data" / "processed" / "raw_rfi.csv"

REPORT_DIR = ROOT / "data" / "processed" / "profiling"

EXPECTED_COLUMNS = [
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


def load_data() -> pd.DataFrame:
    """Load raw CSV without changing original values."""

    print("Loading raw_rfi.csv ...")

    df = pd.read_csv(
        INPUT,
        dtype=str,
        keep_default_na=False,
    )

    print(f"Loaded {len(df)} rows and {len(df.columns)} columns.\n")

    return df


def basic_structure(df: pd.DataFrame) -> None:
    """Inspect basic dataset structure."""

    print("=" * 70)
    print("1. DATASET STRUCTURE")
    print("=" * 70)

    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    print("\nColumns:")

    for i, column in enumerate(df.columns, start=1):
        print(f"{i:>2}. {column}")

    missing_expected = [
        column
        for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    unexpected = [
        column
        for column in df.columns
        if column not in EXPECTED_COLUMNS
    ]

    print("\nSchema check:")

    if not missing_expected and not unexpected:
        print("Schema matches expected raw table.")
    else:
        if missing_expected:
            print(f"Missing columns: {missing_expected}")

        if unexpected:
            print(f"Unexpected columns: {unexpected}")


def completeness_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Measure blank/non-blank values."""

    print("\n" + "=" * 70)
    print("2. COMPLETENESS")
    print("=" * 70)

    results = []

    total = len(df)

    for column in df.columns:

        blank_count = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

        non_blank = total - blank_count

        blank_percentage = (
            blank_count / total * 100
            if total
            else 0
        )

        results.append(
            {
                "column": column,
                "total_rows": total,
                "non_blank": non_blank,
                "blank": blank_count,
                "blank_percent": round(blank_percentage, 2),
            }
        )

    profile = pd.DataFrame(results)

    print(profile.to_string(index=False))

    return profile


def uniqueness_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Count unique values in each field."""

    print("\n" + "=" * 70)
    print("3. UNIQUENESS")
    print("=" * 70)

    results = []

    for column in df.columns:

        non_blank = df.loc[
            df[column].astype(str).str.strip() != "",
            column,
        ]

        results.append(
            {
                "column": column,
                "unique_values": non_blank.nunique(),
                "non_blank_rows": len(non_blank),
            }
        )

    profile = pd.DataFrame(results)

    print(profile.to_string(index=False))

    return profile


def duplicate_profile(df: pd.DataFrame) -> None:
    """Investigate duplicated rows and RFI numbers."""

    print("\n" + "=" * 70)
    print("4. DUPLICATES")
    print("=" * 70)

    full_duplicates = df.duplicated().sum()

    print(f"Exact duplicate rows: {full_duplicates}")

    if "rfi_number" in df.columns:

        valid_rfi = df[
            df["rfi_number"].astype(str).str.strip() != ""
        ]

        duplicate_rfi = valid_rfi[
            valid_rfi.duplicated(
                subset=["rfi_number"],
                keep=False,
            )
        ].sort_values("rfi_number")

        print(
            f"Rows with duplicated RFI numbers: "
            f"{len(duplicate_rfi)}"
        )

        if not duplicate_rfi.empty:

            print("\nDuplicated RFI numbers:")

            columns = [
                "rfi_number",
                "from_party",
                "tasked_to",
                "status_raw",
            ]

            columns = [
                column
                for column in columns
                if column in duplicate_rfi.columns
            ]

            print(
                duplicate_rfi[columns]
                .to_string(index=False)
            )


def categorical_profile(df: pd.DataFrame) -> None:
    """Inspect frequently occurring categorical values."""

    print("\n" + "=" * 70)
    print("5. CATEGORICAL VALUE DISTRIBUTIONS")
    print("=" * 70)

    categorical_columns = [
        "from_party",
        "tasked_to",
        "status_raw",
        "source_file",
    ]

    for column in categorical_columns:

        if column not in df.columns:
            continue

        print(f"\n--- {column} ---")

        values = (
            df[column]
            .value_counts(dropna=False)
            .head(20)
        )

        print(values.to_string())


def date_profile(df: pd.DataFrame) -> None:
    """Investigate Excel serial values without converting them."""

    print("\n" + "=" * 70)
    print("6. DATE_RECEIVED RAW VALUES")
    print("=" * 70)

    if "date_received" not in df.columns:
        print("date_received column not found.")
        return

    values = df["date_received"].astype(str).str.strip()

    blank_count = values.eq("").sum()

    numeric_values = pd.to_numeric(
        values,
        errors="coerce",
    )

    numeric_count = numeric_values.notna().sum()

    non_numeric_count = (
        (~values.eq("")) &
        numeric_values.isna()
    ).sum()

    print(f"Blank values       : {blank_count}")
    print(f"Numeric values     : {numeric_count}")
    print(f"Non-numeric values : {non_numeric_count}")

    if numeric_count:

        print(
            f"Minimum Excel serial: "
            f"{numeric_values.min()}"
        )

        print(
            f"Maximum Excel serial: "
            f"{numeric_values.max()}"
        )

    if non_numeric_count:

        print("\nNon-numeric date values:")

        bad_dates = df.loc[
            (~values.eq("")) &
            numeric_values.isna(),
            [
                "rfi_number",
                "date_received",
            ],
        ]

        print(bad_dates.to_string(index=False))


def text_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Investigate text-field lengths."""

    print("\n" + "=" * 70)
    print("7. TEXT LENGTH ANALYSIS")
    print("=" * 70)

    text_columns = [
        "question",
        "response",
        "notes",
    ]

    results = []

    for column in text_columns:

        if column not in df.columns:
            continue

        lengths = df[column].fillna("").astype(str).str.len()

        non_empty = lengths[lengths > 0]

        results.append(
            {
                "column": column,
                "blank_rows": (lengths == 0).sum(),
                "min_length": (
                    non_empty.min()
                    if not non_empty.empty
                    else 0
                ),
                "avg_length": round(
                    non_empty.mean(),
                    2,
                )
                if not non_empty.empty
                else 0,
                "max_length": (
                    non_empty.max()
                    if not non_empty.empty
                    else 0
                ),
            }
        )

    profile = pd.DataFrame(results)

    print(profile.to_string(index=False))

    return profile


def whitespace_profile(df: pd.DataFrame) -> None:
    """Detect values containing leading or trailing whitespace."""

    print("\n" + "=" * 70)
    print("8. WHITESPACE CHECK")
    print("=" * 70)

    found_issue = False

    for column in df.columns:

        values = df[column].fillna("").astype(str)

        whitespace_count = (
            values.ne(values.str.strip())
        ).sum()

        if whitespace_count > 0:

            found_issue = True

            print(
                f"{column:<25} "
                f"{whitespace_count} values"
            )

    if not found_issue:
        print("No leading/trailing whitespace detected.")


def sample_records(df: pd.DataFrame) -> None:
    """Display a small sample without modifying data."""

    print("\n" + "=" * 70)
    print("9. SAMPLE RECORDS")
    print("=" * 70)

    display_columns = [
        "rfi_number",
        "from_party",
        "tasked_to",
        "date_received",
        "status_raw",
    ]

    display_columns = [
        column
        for column in display_columns
        if column in df.columns
    ]

    print(
        df[display_columns]
        .head(10)
        .to_string(index=False)
    )


def save_reports(
    completeness: pd.DataFrame,
    uniqueness: pd.DataFrame,
    text_lengths: pd.DataFrame,
) -> None:
    """Save profiling results for later inspection."""

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    completeness.to_csv(
        REPORT_DIR / "completeness_profile.csv",
        index=False,
    )

    uniqueness.to_csv(
        REPORT_DIR / "uniqueness_profile.csv",
        index=False,
    )

    text_lengths.to_csv(
        REPORT_DIR / "text_length_profile.csv",
        index=False,
    )

    print("\n" + "=" * 70)
    print("10. REPORT OUTPUT")
    print("=" * 70)

    print(
        f"Profiling reports written to:\n"
        f"{REPORT_DIR.relative_to(ROOT)}"
    )


def main() -> None:

    print("\nUSACE RFI RAW DATA INVESTIGATION")
    print("=" * 70)

    df = load_data()

    basic_structure(df)

    completeness = completeness_profile(df)

    uniqueness = uniqueness_profile(df)

    duplicate_profile(df)

    categorical_profile(df)

    date_profile(df)

    text_lengths = text_profile(df)

    whitespace_profile(df)

    sample_records(df)

    save_reports(
        completeness,
        uniqueness,
        text_lengths,
    )

    print("\nInvestigation completed.")


if __name__ == "__main__":
    main()