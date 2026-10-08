"""Print every table in the RFI DuckDB database.

Reads data/processed/rfi.duckdb and does not change it. Long text is
shortened in the printout so each table stays readable.
"""

from __future__ import annotations

from pathlib import Path

try:
    import duckdb
except ImportError as error:
    raise SystemExit(
        "Install duckdb from requirements.txt before running this script."
    ) from error

ROOT = Path(__file__).resolve().parents[2]
DATABASE = ROOT / "data" / "processed" / "rfi.duckdb"
TABLE_ORDER = (
    "dim_date",
    "dim_party",
    "dim_discipline",
    "dim_issue_type",
    "fact_rfi",
)
SORT_COLUMN = {
    "dim_date": "date_key",
    "dim_party": "party_key",
    "dim_discipline": "discipline_key",
    "dim_issue_type": "issue_type_key",
    "fact_rfi": "rfi_key",
}


def print_progress(done: int, total: int, label: str) -> None:
    percent = 100 if total == 0 else done * 100 // total
    print(f"\r{label}: {percent}% ({done}/{total})", end="", flush=True)


def table_names(connection: duckdb.DuckDBPyConnection) -> list[str]:
    rows = connection.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'main'
          AND table_type = 'BASE TABLE'
        """
    ).fetchall()
    found = {name for (name,) in rows}
    ordered = [name for name in TABLE_ORDER if name in found]
    ordered.extend(sorted(found - set(ordered)))
    return ordered


def show_query(
    connection: duckdb.DuckDBPyConnection,
    title: str,
    sql: str,
    rows: int,
    max_col_width: int = 72,
) -> None:
    print(f"\n{title}")
    connection.sql(sql).show(max_rows=rows, max_width=220, max_col_width=max_col_width)


def main() -> None:
    if not DATABASE.exists():
        raise SystemExit(
            "Missing data/processed/rfi.duckdb. Run src/database/07_load_rfi_duckdb.py first."
        )

    connection = duckdb.connect(str(DATABASE), read_only=True)
    names = table_names(connection)
    if not names:
        connection.close()
        raise SystemExit("The database has no tables.")

    for index, name in enumerate(names, start=1):
        print_progress(index, len(names), "Reading tables")
        print()
        count = connection.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
        sort = SORT_COLUMN.get(name, "1")
        if name == "fact_rfi":
            show_query(
                connection,
                f"{name}  ({count} rows)  keys",
                f"""
                SELECT
                    rfi_key, rfi_id, date_key, from_party_key, tasked_party_key,
                    discipline_key, issue_type_key
                FROM fact_rfi
                ORDER BY {sort}
                """,
                count,
            )
            show_query(
                connection,
                f"{name}  ({count} rows)  status and flags",
                f"""
                SELECT
                    rfi_id, status, response_available,
                    drawing_update_required, spec_update_required,
                    document_update_required, question_word_count, response_word_count
                FROM fact_rfi
                ORDER BY {sort}
                """,
                count,
            )
            show_query(
                connection,
                f"{name}  ({count} rows)  question, response, notes",
                f"""
                SELECT
                    rfi_id,
                    left(replace(question, chr(10), ' '), 60) AS question,
                    left(replace(response, chr(10), ' '), 40) AS response,
                    left(replace(notes, chr(10), ' '), 40) AS notes
                FROM fact_rfi
                ORDER BY {sort}
                """,
                count,
                max_col_width=60,
            )
            continue
        show_query(
            connection,
            f"{name}  ({count} rows)",
            f'SELECT * FROM "{name}" ORDER BY {sort}',
            count,
        )

    connection.close()
    print(f"Showed {len(names)} tables from {DATABASE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
