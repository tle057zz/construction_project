# RFI star schema

`fact_rfi` is the center of the model. Each of its 107 rows is one RFI. Four dimension tables describe the date, the parties, the discipline, and the issue type.

```mermaid
flowchart TB
    dim_date["dim_date<br/>9 dates"]
    dim_party["dim_party<br/>16 parties"]
    fact_rfi["fact_rfi<br/>107 RFIs"]
    dim_discipline["dim_discipline<br/>10 disciplines"]
    dim_issue_type["dim_issue_type<br/>10 issue types"]

    dim_date ---|"date_key"| fact_rfi
    dim_party ---|"from_party_key<br/>tasked_party_key"| fact_rfi
    fact_rfi ---|"discipline_key"| dim_discipline
    fact_rfi ---|"issue_type_key"| dim_issue_type
```

| Table | Rows | Grain |
|---|---:|---|
| `fact_rfi` | 107 | One row per RFI, `RFI-001` to `RFI-107` |
| `dim_date` | 9 | One row per received date |
| `dim_party` | 16 | One row per party name |
| `dim_discipline` | 10 | One row per discipline |
| `dim_issue_type` | 10 | One row per issue type |

## Relationships

Each fact row points at exactly one row in each dimension.

| Fact column | Dimension | Meaning |
|---|---|---|
| `date_key` | `dim_date.date_key` | Date the RFI was received. The key is `YYYYMMDD`. |
| `from_party_key` | `dim_party.party_key` | Party that submitted the RFI. |
| `tasked_party_key` | `dim_party.party_key` | Party tasked to answer the RFI. |
| `discipline_key` | `dim_discipline.discipline_key` | Derived engineering discipline. |
| `issue_type_key` | `dim_issue_type.issue_type_key` | Derived issue type. |

`dim_party` is one list of party names. Submitting and tasked parties are two foreign keys on the fact, so the same party can fill either role.

Question text, response text, notes, status, document-update flags, and word counts stay on `fact_rfi`. They describe that one RFI and are not reused as dimensions.

## Columns

```mermaid
erDiagram
    DIM_DATE ||--o{ FACT_RFI : received_on
    DIM_PARTY ||--o{ FACT_RFI : submitted_by
    DIM_PARTY ||--o{ FACT_RFI : tasked_to
    DIM_DISCIPLINE ||--o{ FACT_RFI : classified_as
    DIM_ISSUE_TYPE ||--o{ FACT_RFI : classified_as

    DIM_DATE {
        int date_key PK
        date date_received
        int calendar_year
        int calendar_month
        int calendar_day
    }

    DIM_PARTY {
        int party_key PK
        string party_name
    }

    DIM_DISCIPLINE {
        int discipline_key PK
        string discipline_name
    }

    DIM_ISSUE_TYPE {
        int issue_type_key PK
        string issue_type_name
    }

    FACT_RFI {
        int rfi_key PK
        string rfi_id
        int date_key FK
        int from_party_key FK
        int tasked_party_key FK
        int discipline_key FK
        int issue_type_key FK
        string question
        string response
        string notes
        string status
        string response_available
        string drawing_update_required
        string spec_update_required
        string document_update_required
        int question_word_count
        int response_word_count
    }
```

The database is `data/processed/rfi.duckdb`, loaded by `src/database/07_load_rfi_duckdb.py` from `data/processed/rfi_features.csv`.
