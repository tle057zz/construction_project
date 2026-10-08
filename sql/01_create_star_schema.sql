-- Build the RFI star schema from rfi_feature_stage.
-- The Python loader creates that staging table and replaces the database on each run.

CREATE OR REPLACE TABLE dim_date AS
SELECT
    CAST(strftime(date_received, '%Y%m%d') AS INTEGER) AS date_key,
    date_received,
    year(date_received) AS calendar_year,
    month(date_received) AS calendar_month,
    day(date_received) AS calendar_day
FROM (
    SELECT DISTINCT CAST(date_received AS DATE) AS date_received
    FROM rfi_feature_stage
    WHERE date_received IS NOT NULL
      AND trim(CAST(date_received AS VARCHAR)) <> ''
) dates;

CREATE OR REPLACE TABLE dim_party AS
SELECT
    row_number() OVER (ORDER BY party_name) AS party_key,
    party_name
FROM (
    SELECT trim(from_party) AS party_name
    FROM rfi_feature_stage
    UNION
    SELECT trim(tasked_to) AS party_name
    FROM rfi_feature_stage
) parties
WHERE party_name IS NOT NULL
  AND party_name <> '';

CREATE OR REPLACE TABLE dim_discipline AS
SELECT
    row_number() OVER (ORDER BY discipline_name) AS discipline_key,
    discipline_name
FROM (
    SELECT DISTINCT trim(discipline) AS discipline_name
    FROM rfi_feature_stage
    WHERE discipline IS NOT NULL
      AND trim(discipline) <> ''
) disciplines;

CREATE OR REPLACE TABLE dim_issue_type AS
SELECT
    row_number() OVER (ORDER BY issue_type_name) AS issue_type_key,
    issue_type_name
FROM (
    SELECT DISTINCT trim(issue_type) AS issue_type_name
    FROM rfi_feature_stage
    WHERE issue_type IS NOT NULL
      AND trim(issue_type) <> ''
) issue_types;

CREATE OR REPLACE TABLE fact_rfi AS
SELECT
    row_number() OVER (ORDER BY stage.rfi_id) AS rfi_key,
    stage.rfi_id,
    dim_date.date_key,
    from_party.party_key AS from_party_key,
    tasked_party.party_key AS tasked_party_key,
    dim_discipline.discipline_key,
    dim_issue_type.issue_type_key,
    stage.question,
    stage.response,
    stage.notes,
    stage.status,
    stage.response_available,
    stage.drawing_update_required,
    stage.spec_update_required,
    stage.document_update_required,
    CAST(stage.question_word_count AS INTEGER) AS question_word_count,
    CAST(stage.response_word_count AS INTEGER) AS response_word_count
FROM rfi_feature_stage AS stage
LEFT JOIN dim_date
    ON dim_date.date_received = CAST(stage.date_received AS DATE)
LEFT JOIN dim_party AS from_party
    ON from_party.party_name = trim(stage.from_party)
LEFT JOIN dim_party AS tasked_party
    ON tasked_party.party_name = trim(stage.tasked_to)
LEFT JOIN dim_discipline
    ON dim_discipline.discipline_name = trim(stage.discipline)
LEFT JOIN dim_issue_type
    ON dim_issue_type.issue_type_name = trim(stage.issue_type);

DROP TABLE rfi_feature_stage;
