"""Load the RFI feature table into a DuckDB star schema.

Reads data/processed/rfi_features.csv, runs sql/01_create_star_schema.sql
and sql/02_quality_checks.sql, and writes data/processed/rfi.duckdb.
The feature CSV is not modified. Each run replaces the database file.
"""

from __future__ import annotations

import csv
from pathlib import Path

try:
    import duckdb
except ImportError as error:
    raise SystemExit(
        "Install duckdb from requirements.txt before running this script."
    ) from error

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / "data" / "processed" / "rfi_features.csv"
DATABASE = ROOT / "data" / "processed" / "rfi.duckdb"
SCHEMA_SQL = ROOT / "sql" / "01_create_star_schema.sql"
CHECKS_SQL = ROOT / "sql" / "02_quality_checks.sql"
RESULTS = ROOT / "data" / "processed" / "validation" / "sql_quality_checks.csv"


def print_progress(done: int, total: int, label: str) -> None:
    percent = 100 if total == 0 else done * 100 // total
    print(f"\r{label}: {percent}% ({done}/{total})", end="", flush=True)


def statements(sql: str) -> list[str]:
    parts = []
    for chunk in sql.split(";"):
        lines = [
            line
            for line in chunk.splitlines()
            if line.strip() and not line.strip().startswith("--")
        ]
        text = "\n".join(lines).strip()
        if text:
            parts.append(text)
    return parts


def run_sql(connection: duckdb.DuckDBPyConnection, path: Path) -> duckdb.DuckDBPyConnection | None:
    result = None
    for statement in statements(path.read_text(encoding="utf-8")):
        result = connection.execute(statement)
    return result


def replace_database() -> None:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    for path in (DATABASE, Path(str(DATABASE) + ".wal")):
        if path.exists():
            path.unlink()


def write_results(rows: list[tuple[str, str, str]]) -> None:
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["check", "result", "detail"])
        writer.writerows(rows)


def main() -> None:
    steps = 3
    replace_database()
    print_progress(1, steps, "Preparing database")

    connection = duckdb.connect(str(DATABASE))
    csv_path = str(FEATURES).replace("'", "''")
    connection.execute(
        "CREATE TABLE rfi_feature_stage AS "
        f"SELECT * FROM read_csv_auto('{csv_path}', header = true)"
    )
    print_progress(2, steps, "Preparing database")

    run_sql(connection, SCHEMA_SQL)
    result = run_sql(connection, CHECKS_SQL)
    rows = [(str(check), str(status), str(detail)) for check, status, detail in result.fetchall()]
    print_progress(3, steps, "Preparing database")
    print()

    write_results(rows)
    counts = connection.execute(
        """
        SELECT 'dim_date' AS table_name, count(*) FROM dim_date
        UNION ALL SELECT 'dim_party', count(*) FROM dim_party
        UNION ALL SELECT 'dim_discipline', count(*) FROM dim_discipline
        UNION ALL SELECT 'dim_issue_type', count(*) FROM dim_issue_type
        UNION ALL SELECT 'fact_rfi', count(*) FROM fact_rfi
        ORDER BY table_name
        """
    ).fetchall()
    connection.close()

    failed = 0
    for check, status, detail in rows:
        print(f"{status}  {check}: {detail}")
        if status == "FAIL":
            failed += 1
    print(f"Wrote {DATABASE.relative_to(ROOT)}")
    for table_name, count in counts:
        print(f"  {count:3} {table_name}")
    print(f"Wrote {RESULTS.relative_to(ROOT)}")
    if failed:
        raise SystemExit(f"{failed} check(s) failed")
    print(f"All {len(rows)} checks passed")


if __name__ == "__main__":
    main()
