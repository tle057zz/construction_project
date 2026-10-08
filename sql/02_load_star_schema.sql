-- Load dimensions and the fact from staging_rfi.
-- staging_rfi is created by the Python runner from rfi_features.csv.

INSERT INTO dim_date (
    date_key,
    full_date,
    calendar_year,
    calendar_month,
    day_of_month,
    month_name
)
SELECT DISTINCT
    year(received) * 10000 + month(received) * 100 + day(received) AS date_key,
    received AS full_date,
    year(received) AS calendar_year,
    month(received) AS calendar_month,
    day(received) AS day_of_month,
    monthname(received) AS month_name
FROM (
    SELECT CAST(date_received AS DATE) AS received
    FROM staging_rfi
) dates
ORDER BY full_date;

INSERT INTO dim_party (party_key, party_name)
SELECT
    row_number() OVER (ORDER BY party_name) AS party_key,
    party_name
FROM (
    SELECT from_party AS party_name FROM staging_rfi
    UNION
    SELECT tasked_to AS party_name FROM staging_rfi
) parties
WHERE trim(party_name) <> '';

INSERT INTO dim_discipline (discipline_key, discipline_name)
SELECT
    row_number() OVER (ORDER BY discipline_name) AS discipline_key,
    discipline_name
FROM (
    SELECT DISTINCT discipline AS discipline_name
    FROM staging_rfi
    WHERE trim(discipline) <> ''
) disciplines;

INSERT INTO dim_issue_type (issue_type_key, issue_type_name)
SELECT
    row_number() OVER (ORDER BY issue_type_name) AS issue_type_key,
    issue_type_name
FROM (
    SELECT DISTINCT issue_type AS issue_type_name
    FROM staging_rfi
    WHERE trim(issue_type) <> ''
) issue_types;

INSERT INTO fact_rfi (
    rfi_key,
    rfi_id,
    date_key,
    from_party_key,
    tasked_party_key,
    discipline_key,
    issue_type_key,
    question,
    response,
    notes,
    status,
    response_available,
    drawing_update_required,
    spec_update_required,
    document_update_required,
    question_word_count,
    response_word_count
)
SELECT
    row_number() OVER (ORDER BY stage.rfi_id) AS rfi_key,
    stage.rfi_id,
    dates.date_key,
    from_party.party_key,
    tasked_party.party_key,
    discipline.discipline_key,
    issue.issue_type_key,
    stage.question,
    stage.response,
    stage.notes,
    stage.status,
    stage.response_available,
    stage.drawing_update_required,
    stage.spec_update_required,
    stage.document_update_required,
    CAST(stage.question_word_count AS INTEGER),
    CAST(stage.response_word_count AS INTEGER)
FROM staging_rfi AS stage
JOIN dim_date AS dates
    ON dates.full_date = CAST(stage.date_received AS DATE)
JOIN dim_party AS from_party
    ON from_party.party_name = stage.from_party
JOIN dim_party AS tasked_party
    ON tasked_party.party_name = stage.tasked_to
JOIN dim_discipline AS discipline
    ON discipline.discipline_name = stage.discipline
JOIN dim_issue_type AS issue
    ON issue.issue_type_name = stage.issue_type;
