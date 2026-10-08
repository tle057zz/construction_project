-- One row per check. PASS means the star schema still matches the feature table rules.

SELECT
    'fact_row_count' AS check_name,
    CASE WHEN count(*) = 107 THEN 'PASS' ELSE 'FAIL' END AS result,
    count(*) || ' rows' AS detail
FROM fact_rfi

UNION ALL

SELECT
    'duplicate_rfi_id',
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    count(*) || ' duplicated identifiers'
FROM (
    SELECT rfi_id
    FROM fact_rfi
    GROUP BY rfi_id
    HAVING count(*) > 1
) duplicates

UNION ALL

SELECT
    'rfi_id_sequence',
    CASE
        WHEN (
            SELECT list(rfi_id ORDER BY rfi_id) FROM fact_rfi
        ) = (
            SELECT list(printf('RFI-%03d', n) ORDER BY n)
            FROM range(1, 108) AS numbers(n)
        )
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    (SELECT min(rfi_id) || ' to ' || max(rfi_id) FROM fact_rfi)

UNION ALL

SELECT
    'missing_dimension_keys',
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    count(*) || ' facts missing a dimension key'
FROM fact_rfi
WHERE date_key IS NULL
   OR from_party_key IS NULL
   OR tasked_party_key IS NULL
   OR discipline_key IS NULL
   OR issue_type_key IS NULL

UNION ALL

SELECT
    'blank_question',
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    count(*) || ' blank'
FROM fact_rfi
WHERE question IS NULL
   OR trim(question) = ''

UNION ALL

SELECT
    'invalid_status',
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    count(*) || ' outside Answered and Open'
FROM fact_rfi
WHERE status NOT IN ('Answered', 'Open')
