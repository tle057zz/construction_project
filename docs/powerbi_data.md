# Power BI drawing data

The files in `data/processed/powerbi` are the star schema exported from `data/processed/rfi.duckdb` by `src/database/09_export_powerbi.py`. Load `rfi_star_schema.xlsx` (one sheet per table) or the five CSVs beside it. Each run of that script replaces the same files.

Every chart is a count, a filter, or a text lookup of these 107 RFIs. The grain of `fact_rfi` is one row per RFI, `RFI-001` through `RFI-107`. Keys `rfi_key` 1 through 107 match that order. No fact key is missing from a dimension, and every dimension row is used at least once.

```text
dim_date          9 rows     date the RFI was received
dim_party        16 rows     one name, used as submitter or as tasked party
dim_discipline   10 rows     derived engineering discipline
dim_issue_type   10 rows     derived issue type
fact_rfi        107 rows     one RFI
```

Relationships, all many-to-one from the fact:

| Fact column | Dimension column | Role |
|---|---|---|
| `date_key` | `dim_date.date_key` | Received date. The key is `YYYYMMDD`. |
| `from_party_key` | `dim_party.party_key` | Party that submitted the RFI. |
| `tasked_party_key` | `dim_party.party_key` | Party tasked to answer. |
| `discipline_key` | `dim_discipline.discipline_key` | Discipline. |
| `issue_type_key` | `dim_issue_type.issue_type_key` | Issue type. |

`dim_party` is one list. Submitter and tasked party are two relationships to that same list. In this extract the two roles do not share a name: six contractors submit, and ten government or design parties are tasked.

Discipline, issue type, status, and the document flags are derived in `src/features/06_build_rfi_features.py`. They are labels for drawing, not the blank Status column from the workbook.

## Dates

Nine received dates, all in September 2026. `calendar_year` is 2026 on every row and `calendar_month` is 9 on every row, so a month chart has one bar. A day chart is the useful date visual.

| Date | RFIs |
|---|---:|
| 2026-09-01 | 1 |
| 2026-09-02 | 6 |
| 2026-09-04 | 67 |
| 2026-09-10 | 11 |
| 2026-09-14 | 2 |
| 2026-09-15 | 1 |
| 2026-09-16 | 8 |
| 2026-09-17 | 3 |
| 2026-09-21 | 8 |

`date_received` is a real date (`2026-09-01`). `date_key` is the integer `20260901`.

## Parties

Submitters (`from_party_key`), 6 names, 107 RFIs:

| Party | RFIs |
|---|---:|
| DAVID BOLAND, INC | 71 |
| Carbon Recall Chattanooga | 11 |
| Willdan | 8 |
| Dobco, Inc. | 8 |
| Richard Group LCC | 8 |
| Schweitzer Engineering Laboratories, Inc. | 1 |

Tasked parties (`tasked_party_key`), 10 names:

| Party | RFIs |
|---|---:|
| AE | 66 |
| CT | 15 |
| PM | 9 |
| JBMDL | 8 |
| AE/JBMDL | 4 |
| CT/PM | 1 |
| USACE DB | 1 |
| AE/PM | 1 |
| AE/JBMDL/PM | 1 |
| JBMDL/AE | 1 |

A submitter chart and a tasked-party chart need two relationships to `dim_party`. One active relationship cannot serve both.

## Discipline

| Discipline | RFIs |
|---|---:|
| Electrical | 40 |
| Other | 24 |
| General | 15 |
| Civil | 9 |
| Structural | 5 |
| Mechanical | 4 |
| Architectural | 3 |
| Quality / Inspection | 3 |
| Controls / SCADA | 2 |
| Cybersecurity | 2 |

Electrical is 40 of 107. A bar chart will be dominated by that one category. `Other` and `General` are real labels from the feature rules, not leftovers from a failed join.

## Issue type

| Issue type | RFIs |
|---|---:|
| Specification Clarification | 62 |
| Compliance Requirement | 11 |
| Missing Information | 11 |
| Design Clarification | 6 |
| Inspection / Quality | 6 |
| Material Requirement | 4 |
| Interface Coordination | 3 |
| Drawing Conflict | 2 |
| Constructability | 1 |
| Scope Gap | 1 |

Specification Clarification is 62 of 107. Constructability is `RFI-023`. Scope Gap is `RFI-096`.

## Status and response

| Status | RFIs | `response_available` | Response text |
|---|---:|---|---|
| Answered | 99 | `true` | Present |
| Open | 8 | `false` | Blank, word count 0 |

Status is Answered when the response cell has text, and Open when it is blank. `response_available` repeats that split as the text values `true` and `false`. The eight open IDs are `RFI-086`, `RFI-092`, `RFI-093`, `RFI-095`, `RFI-096`, `RFI-100`, `RFI-106`, and `RFI-107`.

Question text is present on all 107 rows. Length runs from 66 to 2,203 characters, and the word count runs from 9 to 335 with a median of 69. Response word count runs from 0 to 109 with a median of 16. Those two word-count columns are the measures for a length visual. Question and response themselves belong in a table or a tooltip, not in an aggregated chart.

## Document updates

The three flags are `Yes`, `No`, or `Unknown`. They are read from `notes`.

| Flag | Yes | No | Unknown |
|---|---:|---:|---:|
| Drawing update required | 18 | 51 | 38 |
| Spec update required | 17 | 51 | 39 |
| Document update required | 19 | 51 | 37 |

Document update is Yes when either drawing or spec is Yes. The 19 Yes rows are 16 that update both, 2 that update a drawing only, and 1 that updates a specification only. The 51 No rows are the notes that say no specification or drawing update is required. Unknown means the note is blank or only says an attachment was sent. A chart that treats Unknown as No will understate the open question.

`notes` itself has seven distinct values, so it is a short label, not a long narrative:

| Notes | RFIs |
|---|---:|
| No spec/drawing update required. | 51 |
| (blank) | 35 |
| Updated spec/dwg included | 15 |
| Correct attachment sent to USACE for inclusion in the set. | 2 |
| Drawing update provided as part of RFI-47 | 2 |
| Updated spec/dwg included/ Redundant with RFI-08 | 1 |
| Updated spec included | 1 |

## What each visual can use

| Visual | Fields |
|---|---|
| RFI count | Count of `fact_rfi.rfi_id` |
| Received by day | `dim_date.date_received` |
| Submitter | `dim_party.party_name` through `from_party_key` |
| Tasked party | `dim_party.party_name` through `tasked_party_key` |
| Discipline mix | `dim_discipline.discipline_name` |
| Issue-type mix | `dim_issue_type.issue_type_name` |
| Open against answered | `fact_rfi.status` |
| Document impact | `document_update_required`, with Unknown kept as its own category |
| Question and response length | `question_word_count`, `response_word_count` |
| RFI detail | `rfi_id`, `question`, `response`, `notes` |
