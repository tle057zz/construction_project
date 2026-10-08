-- Quality checks for the loaded star schema.
-- Each row is one check. A passing database returns PASS on every row.

SELECT
    'row_count' AS check_name,
    CASE WHEN COUNT(*) = 107 THEN 'PASS' ELSE 'FAIL' END AS result,
    COUNT(*) || ' fact rows' AS detail
FROM fact_rfi

UNION ALL

SELECT
    'duplicate_rfi_id',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*) || ' ids with more than one row'
FROM (
    SELECT rfi_id
    FROM fact_rfi
    GROUP BY rfi_id
    HAVING COUNT(*) > 1
) duplicates

UNION ALL

SELECT
    'question_present',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*) || ' blank questions'
FROM fact_rfi
WHERE trim(question) = ''

UNION ALL

SELECT
    'date_key_matched',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*) || ' facts without a date'
FROM fact_rfi AS fact
LEFT JOIN dim_date AS dim
    ON fact.date_key = dim.date_key
WHERE dim.date_key IS NULL

UNION ALL

SELECT
    'from_party_matched',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*) || ' facts without a submitting party'
FROM fact_rfi AS fact
LEFT JOIN dim_party AS dim
    ON fact.from_party_key = dim.party_key
WHERE dim.party_key IS NULL

UNION ALL

SELECT
    'tasked_party_matched',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*) || ' facts without a tasked party'
FROM fact_rfi AS fact
LEFT JOIN dim_party AS dim
    ON fact.tasked_party_key = dim.party_key
WHERE dim.party_key IS NULL

UNION ALL

SELECT
    'discipline_matched',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*) || ' facts without a discipline'
FROM fact_rfi AS fact
LEFT JOIN dim_discipline AS dim
    ON fact.discipline_key = dim.discipline_key
WHERE dim.discipline_key IS NULL

UNION ALL

SELECT
    'issue_type_matched',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*) || ' facts without an issue type'
FROM fact_rfi AS fact
LEFT JOIN dim_issue_type AS dim
    ON fact.issue_type_key = dim.issue_type_key
WHERE dim.issue_type_key IS NULL

UNION ALL

SELECT
    'status_values',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*) || ' rows outside Answered and Open'
FROM fact_rfi
WHERE status NOT IN ('Answered', 'Open')

UNION ALL

SELECT
    'status_matches_response',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    COUNT(*) || ' status mismatches'
FROM fact_rfi
WHERE NOT (
    (status = 'Answered' AND response_available = 'Yes' AND trim(response) <> '')
    OR (status = 'Open' AND response_available = 'No' AND trim(response) = '')
);
