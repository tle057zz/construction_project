
# Digital Engineering RFI Analytics & AI Platform
## Detailed End-to-End Project Plan

---

# 1. Project Title

**Digital Engineering RFI Analytics & AI Platform using Python, SQL, Power BI, Databricks, MLflow and Generative AI**

---

# 2. Project Purpose

This project is designed as a portfolio case study for Digital Engineering, Project Systems, Data, Automation and AI-focused roles in construction and infrastructure.

The project uses a **real USACE RFI log** as the source dataset and develops it into a complete digital engineering solution.

The project will demonstrate:

- RFI data ingestion
- Data cleaning and validation
- SQL data modelling
- Power BI reporting
- Python automation
- Digital engineering workflow design
- Databricks analytics
- Machine learning
- NLP classification
- RFI summarisation
- Document-impact prediction
- MLflow experiment tracking
- Model Registry
- AI-powered RFI search and question answering
- Responsible AI and evaluation

---

# 3. Source Dataset

## Dataset

**USACE RFI Log – Power Generation with Microgrid Project**

Source file:

```text
RFI log for posting 9.23.26.xlsx
```

The workbook contains approximately 111 real RFI records.

Observed source columns:

```text
RFI #
FROM
TASKED
DATE RECEIVED
QUESTION
RESPONSE
NOTES
Status
```

The questions include genuine engineering and project-delivery topics such as:

```text
Battery Energy Storage Systems
Electrical systems
SCADA
Cybersecurity
Civil works
Mechanical systems
Natural gas
Specifications
Drawings
Special inspections
Coating requirements
Design clarifications
```

---

# 4. Final Project Objective

Build a system that transforms unstructured and semi-structured RFI records into a governed project analytics and AI solution.

Final architecture:

```text
                    Real USACE RFI Excel
                              |
                              v
                        Python Ingestion
                              |
                              v
                      Raw / Clean RFI Data
                              |
                              v
                         SQL Database
                              |
                  +-----------+-----------+
                  |                       |
                  v                       v
              Power BI                Databricks
                                          |
                         +----------------+----------------+
                         |                |                |
                         v                v                v
                  Classification     Summarisation    Impact Model
                         |                |                |
                         +----------------+----------------+
                                          |
                                          v
                                       MLflow
                                          |
                                          v
                                   Model Registry
                                          |
                                          v
                                    RFI AI Copilot
```

---

# 5. Business Problem

Construction and infrastructure projects generate large volumes of RFIs.

Typical problems include:

- RFIs are stored in spreadsheets, emails or CDE systems.
- Engineering questions are difficult to classify consistently.
- Project managers lack clear visibility into issue trends.
- Repeated clarification topics are difficult to identify.
- Drawing and specification updates are not always easy to track.
- Long RFI descriptions and responses are time-consuming to review.
- There is limited ability to search RFIs using natural language.
- Project teams may not have a consolidated dashboard for monitoring RFI activity.

The project will address these problems with automation, analytics and AI.

---

# 6. Project Deliverables

The final portfolio should contain:

```text
1. Cleaned RFI dataset
2. Python ETL scripts
3. SQL database
4. SQL schema
5. Power BI dashboard
6. RFI classification model
7. RFI summarisation pipeline
8. Document-impact prediction model
9. MLflow experiments
10. Registered ML models
11. Databricks notebooks
12. RFI Copilot
13. AI evaluation results
14. Architecture diagram
15. Data model diagram
16. GitHub README
17. Demo screenshots
18. Optional demo video
```

---

# 7. Recommended Technology Stack

## Data Engineering

```text
Python
pandas
PySpark
SQL
Databricks
Delta Lake
```

## Database

Choose one:

```text
PostgreSQL
SQL Server
Azure SQL
```

Recommended:

```text
PostgreSQL
```

for local development.

## Business Intelligence

```text
Power BI
DAX
```

## Machine Learning

```text
scikit-learn
XGBoost
MLflow
SHAP
```

## Generative AI

```text
LLM
Embeddings
RAG
Vector Search / Databricks AI Search
Prompt Engineering
Evaluation
Guardrails
```

## Engineering Tools

```text
Git
GitHub
VS Code
Databricks
draw.io
```

---

# 8. Repository Structure

```text
digital-engineering-rfi-ai/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── rfi_log.xlsx
│   ├── processed/
│   │   └── rfi_clean.csv
│   └── reference/
│
├── src/
│   ├── ingestion/
│   │   └── load_rfi_excel.py
│   ├── cleaning/
│   │   └── clean_rfi.py
│   ├── validation/
│   │   └── validate_rfi.py
│   ├── features/
│   │   └── build_rfi_features.py
│   ├── database/
│   │   └── load_postgres.py
│   └── utils/
│
├── sql/
│   ├── schema.sql
│   ├── views.sql
│   └── quality_checks.sql
│
├── databricks/
│   ├── 01_ingest_clean_rfi.py
│   ├── 02_feature_engineering.py
│   ├── 03_rfi_classification.py
│   ├── 04_issue_type_classification.py
│   ├── 05_document_impact_model.py
│   ├── 06_rfi_summarisation.py
│   ├── 07_rfi_embeddings.py
│   ├── 08_rfi_copilot.py
│   └── 09_ai_evaluation.py
│
├── ml/
│   ├── experiments/
│   ├── evaluation/
│   └── inference/
│
├── ai/
│   ├── prompts/
│   ├── evaluation/
│   └── rag/
│
├── powerbi/
│   ├── screenshots/
│   └── documentation/
│
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── business_case.md
│   └── model_card.md
│
└── tests/
```

---

# 9. PHASE 1 - Raw Data Setup

## Objective

Preserve the original USACE workbook and create a reproducible raw-data layer.

## Tasks

1. Create project repository.
2. Create `data/raw/`.
3. Copy the original Excel file into the folder.
4. Rename it to:

```text
rfi_log.xlsx
```

5. Do not modify the original workbook manually.

## Milestone

```text
Original RFI source stored unchanged in project.
```

---

# 10. PHASE 2 - Raw Data Profiling

## Objective

Understand the workbook before cleaning it.

## Inspect

```text
Number of rows
Number of columns
Header location
Blank title rows
Null values
Duplicate RFI numbers
Date formats
Status completeness
Question length
Response completeness
Notes content
Unique FROM values
Unique TASKED values
```

## Example Python

```python
import pandas as pd

df = pd.read_excel("data/raw/rfi_log.xlsx")

print(df.shape)
print(df.columns)
print(df.head())
print(df.isnull().sum())
```

Because the workbook may include introductory rows before the real header, detect the correct header row instead of assuming row 1.

## Milestone

Create:

```text
docs/data_profiling.md
```

with source observations.

---

# 11. PHASE 3 - Raw RFI Table

## Objective

Create a clean raw table while preserving original values.

Proposed raw schema:

```text
raw_rfi
-----------------------------
rfi_number
from_party
tasked_to
date_received
question
response
notes
status_raw
source_file
ingestion_timestamp
```

Do not add interpretation yet.

## Example output

```text
RFI-001
Contractor A
AE
2026-08-01
Question text...
Response text...
Updated drawing required
NULL
rfi_log.xlsx
2026-10-02 10:00
```

---

# 12. PHASE 4 - RFI Cleaning

## Objective

Create a reliable analytical RFI table.

Clean:

```text
RFI IDs
Party names
Dates
Whitespace
Encoding
Blank values
Duplicate records
Status values
Question text
Response text
Notes text
```

Create:

```text
rfi_clean
```

with:

```text
rfi_id
from_party
tasked_to
date_received
question
response
notes
status
response_available
```

## Derived status rule

For example:

```text
if response exists:
    status = "Answered"
else:
    status = "Open"
```

If an explicit source status exists, preserve it and prefer the real source value.

---

# 13. PHASE 5 - Engineering Enrichment

## Objective

Create analytical fields that do not exist directly in the source.

Add:

```text
discipline
issue_type
reference_type
reference_id
priority
drawing_update_required
spec_update_required
document_update_required
response_available
question_word_count
response_word_count
```

---

# 14. Discipline Classification

Recommended categories:

```text
Electrical
Mechanical
Civil
Structural
Controls / SCADA
Cybersecurity
Architectural
Quality / Inspection
General
Other
```

Initially classify manually or with rules.

Example:

```python
if "battery" in text or "electrical" in text:
    discipline = "Electrical"
elif "gas line" in text:
    discipline = "Mechanical"
```

Later replace this with ML / AI classification.

---

# 15. Issue Type Classification

Recommended RFI issue categories:

```text
Design Clarification
Drawing Conflict
Specification Clarification
Missing Information
Scope Gap
Constructability
Compliance Requirement
Material Requirement
Interface Coordination
Inspection / Quality
Other
```

These categories will become the target labels for the AI model.

---

# 16. Document Reference Extraction

Extract references such as:

```text
Drawing numbers
Specification sections
Sheet numbers
Technical clauses
Equipment IDs
```

Create:

```text
reference_type
reference_number
```

Example:

```text
Drawing
CS112
```

or:

```text
Specification
26 32 13
```

---

# 17. Document Update Classification

Use the NOTES and RESPONSE fields to derive:

```text
drawing_update_required
spec_update_required
```

Possible values:

```text
Yes
No
Unknown
```

Then derive:

```text
document_update_required
```

Example logic:

```text
Drawing update only
Specification update only
Both
No update
Unknown
```

---

# 18. PHASE 6 - SQL Database

## Objective

Load structured RFI data into a relational database.

Recommended:

```text
PostgreSQL
```

Create:

```text
dim_date
dim_discipline
dim_issue_type
dim_party
fact_rfi
```

---

# 19. SQL Star Schema

```text
                   dim_date
                      |
                      |
dim_party ------ fact_rfi ------ dim_discipline
                      |
                      |
                dim_issue_type
```

---

# 20. fact_rfi

Suggested columns:

```text
rfi_key
rfi_id
date_key
from_party_key
discipline_key
issue_type_key

question
response
notes

status
response_available

drawing_update_required
spec_update_required

question_word_count
response_word_count
```

---

# 21. SQL Quality Checks

Examples:

```sql
SELECT rfi_id, COUNT(*)
FROM fact_rfi
GROUP BY rfi_id
HAVING COUNT(*) > 1;
```

Check:

```text
Duplicate RFI IDs
Null dates
Missing questions
Missing dimensions
Invalid status values
```

---

# 22. PHASE 7 - Power BI Dashboard

## Objective

Build the core recruiter-facing dashboard before AI.

Power BI reads from SQL.

Architecture:

```text
SQL
 ↓
Power BI
```

---

# 23. Power BI Page 1 - Executive RFI Overview

KPI cards:

```text
Total RFIs
Answered RFIs
Open RFIs
Response Rate %
RFIs Requiring Document Update
Unique Engineering Disciplines
```

Visuals:

```text
RFI Trend
RFI by Discipline
RFI by Issue Type
RFI by Submitter
Document Update Requirement
```

---

# 24. Power BI Page 2 - Engineering Analysis

Show:

```text
RFIs by Engineering Discipline
Top RFI Categories
Drawing-related RFIs
Specification-related RFIs
Questions by technical topic
```

Add drill-through to individual RFI details.

---

# 25. Power BI Page 3 - Document Control Impact

KPIs:

```text
Drawing Updates Required
Specification Updates Required
Both Required
No Update Required
```

Visuals:

```text
Document impact by discipline
Document impact by issue type
Update requirements over time
```

This page is particularly relevant to CDE / EDMS roles.

---

# 26. Power BI Page 4 - Detailed RFI Register

Table:

```text
RFI ID
Date
From
Tasked To
Discipline
Issue Type
Status
Document Update
Question Summary
```

Add slicers:

```text
Date
Discipline
Issue Type
Status
Submitter
Document Impact
```

---

# 27. PHASE 8 - Databricks Setup

## Objective

Extend the project from analytics into Data + AI.

Create Databricks catalog:

```text
digital_engineering
```

Schemas:

```text
digital_engineering.bronze
digital_engineering.silver
digital_engineering.gold
digital_engineering.ml
digital_engineering.ai
```

---

# 28. Databricks Bronze

Load the original / cleaned RFI data as Delta.

Tables:

```text
bronze.rfi_raw
```

Include:

```text
source_file
ingestion_timestamp
```

---

# 29. Databricks Silver

Create:

```text
silver.rfi_clean
```

Include cleaned and standardised RFI fields.

---

# 30. Databricks Gold

Create:

```text
gold.rfi_analytics
```

Fields:

```text
rfi_id
date_received
from_party
tasked_to
discipline
issue_type
status
question
response
notes
drawing_update_required
spec_update_required
document_update_required
```

---

# 31. PHASE 9 - AI Model 1: Discipline Classification

## Business Objective

Automatically identify the engineering discipline for a new RFI.

Input:

```text
RFI question
```

Output:

```text
Electrical
Mechanical
Civil
Structural
Controls / SCADA
Cybersecurity
etc.
```

---

# 32. Baseline Model

Start with:

```text
TF-IDF
+
Logistic Regression
```

Pipeline:

```text
RFI question
   ↓
Text cleaning
   ↓
TF-IDF
   ↓
Logistic Regression
   ↓
Discipline
```

---

# 33. Advanced Classification Model

Compare against:

```text
Sentence embeddings + classifier
LLM zero-shot classification
LLM few-shot classification
```

Track results.

---

# 34. Classification Evaluation

Use:

```text
Accuracy
Precision
Recall
F1
Confusion Matrix
```

Important:

Because the dataset is small, use:

```text
Stratified cross-validation
Manual review
```

Do not pretend the model is production-ready purely because it achieved a flattering number on 111 records.

---

# 35. MLflow Tracking

Create experiment:

```text
rfi_discipline_classification
```

Track:

```text
Model type
Parameters
Feature method
Training set
Accuracy
Precision
Recall
F1
Artifacts
```

---

# 36. Model Registry

Register the selected model.

Example:

```text
digital_engineering.ml.rfi_discipline_classifier
```

Versions:

```text
v1
TF-IDF Logistic Regression

v2
Embedding Classifier

v3
LLM Classification
```

---

# 37. PHASE 10 - AI Model 2: Issue Type Classification

## Objective

Automatically classify the reason for an RFI.

Target:

```text
Design Clarification
Drawing Conflict
Specification Clarification
Missing Information
Scope Gap
Constructability
Compliance
etc.
```

Input:

```text
question
+
optional notes
```

Output:

```text
issue_type
confidence
```

---

# 38. PHASE 11 - AI Model 3: Document Impact Prediction

## Objective

Predict whether an RFI will require:

```text
Drawing update
Specification update
Both
No update
```

Features:

```text
Question text
Response text
Discipline
Issue type
References
```

Target:

```text
document_update_required
```

This is valuable because the source NOTES field already provides evidence for some document updates.

---

# 39. Document Impact Metrics

Use:

```text
Accuracy
Precision
Recall
F1
```

Pay extra attention to recall for:

```text
Update Required
```

because missing a document-impacting RFI is more important than an occasional false positive.

---

# 40. PHASE 12 - RFI Summarisation

## Objective

Create a concise business summary for long RFI questions.

Input:

```text
Full RFI question
```

Output:

```text
1-2 sentence summary
```

Example:

```text
Original:
Long engineering question...

Summary:
Contractor requests clarification regarding the
required battery energy storage system capacity
because the specification and electrical drawings
appear inconsistent.
```

Store:

```text
rfi_short_summary
```

---

# 41. Summarisation Guardrails

The summary must:

```text
Use only information from the RFI
Not invent project facts
Not invent schedule or cost impacts
Preserve technical meaning
Mention uncertainty where appropriate
```

---

# 42. PHASE 13 - Embeddings and Semantic Search

## Objective

Allow users to find similar RFIs using meaning rather than keywords.

Convert:

```text
question
response
summary
```

into embeddings.

Store them using:

```text
Databricks Vector Search / AI Search
```

---

# 43. Semantic Search Examples

User searches:

```text
battery capacity discrepancy
```

System should find semantically related RFIs even if the exact phrase is different.

Other examples:

```text
SCADA integration
drawing conflict
natural gas routing
cybersecurity requirement
special inspections
```

---

# 44. PHASE 14 - RFI AI Copilot

## Objective

Build a natural-language assistant for project teams.

Architecture:

```text
User
 ↓
RFI Copilot
 ↓
+-----------------------+
|                       |
SQL Analytics       Semantic Search
|                       |
Gold RFI Data       Vector Index
|                       |
+-----------+-----------+
            |
            v
       LLM Response
```

---

# 45. Copilot Questions

Examples:

```text
How many electrical RFIs are there?

Which RFIs mention battery systems?

Summarise all SCADA-related RFIs.

Which disciplines generate the most clarifications?

Which RFIs required drawing updates?

What are the most common issue categories?

Show RFIs related to specification conflicts.

What are the recurring technical themes?
```

---

# 46. Copilot Tool Design

Give the agent explicit tools.

```text
Tool 1 - SQL Analytics
Tool 2 - Semantic RFI Search
Tool 3 - RFI Summarisation
Tool 4 - Classification Lookup
Tool 5 - Document Impact Lookup
```

Avoid unrestricted database access.

---

# 47. PHASE 15 - AI Evaluation

Create an evaluation dataset.

Schema:

```text
question
expected_answer
expected_rfi_ids
expected_category
answerable
```

---

# 48. Example Evaluation Questions

```text
Which RFIs mention SCADA?

Expected:
Known SCADA-related RFI IDs

Which RFI categories are most common?

Expected:
SQL-derived counts

What does RFI 42 ask?

Expected:
Grounded summary

What was the project profit margin?

Expected:
Out of scope
```

---

# 49. AI Evaluation Metrics

Track:

```text
Answer correctness
Groundedness
Retrieval accuracy
RFI ID accuracy
Hallucination rate
Classification accuracy
Out-of-scope rejection
Latency
```

---

# 50. PHASE 16 - Responsible AI

Document:

```text
Human review
Source grounding
Role-based access
Prompt logging
Model versioning
Data lineage
Confidence thresholds
Out-of-scope handling
Hallucination monitoring
```

The AI should support project teams, not make binding engineering decisions.

---

# 51. PHASE 17 - Optional API Layer

Add FastAPI.

Endpoints:

```text
GET /api/rfis
GET /api/rfis/{id}
POST /api/classify
POST /api/summarise
POST /api/search
```

This demonstrates:

```text
Python
software development
REST APIs
system integration
```

---

# 52. Optional CDE Integration

Later integrate with:

```text
SharePoint
Microsoft Graph API
```

Possible workflow:

```text
New RFI uploaded
     ↓
Graph API
     ↓
Python
     ↓
Databricks classification
     ↓
SQL
     ↓
Power BI
```

---

# 53. Final Architecture

```text
                     USACE RFI Workbook
                            |
                            v
                       Python ETL
                            |
                  +---------+---------+
                  |                   |
                  v                   v
            PostgreSQL           Databricks
                  |                   |
                  v             Bronze / Silver
             Power BI                 |
                                      v
                                     Gold
                                      |
                  +-------------------+-------------------+
                  |                   |                   |
                  v                   v                   v
             Discipline          Issue Type        Document Impact
             Classifier          Classifier           Model
                  |                   |                   |
                  +-------------------+-------------------+
                                      |
                                      v
                                   MLflow
                                      |
                                      v
                               Model Registry
                                      |
                   +------------------+------------------+
                   |                                     |
                   v                                     v
             Summarisation                       Semantic Search
                   |                                     |
                   +------------------+------------------+
                                      |
                                      v
                                  RFI Copilot
```

---

# 54. Recommended Build Order

Follow this order exactly.

## Stage 1

```text
Download / preserve RFI workbook
Create repository
Profile raw data
```

## Stage 2

```text
Python cleaning
Raw table
Clean RFI table
```

## Stage 3

```text
Manual enrichment
Discipline labels
Issue type labels
Document impact labels
```

## Stage 4

```text
PostgreSQL
Star schema
Data quality checks
```

## Stage 5

```text
Power BI
Executive RFI Dashboard
Engineering Analysis
Document Impact
Detailed Register
```

## Stage 6

```text
Databricks setup
Bronze
Silver
Gold
```

## Stage 7

```text
Discipline classifier
MLflow
Model Registry
```

## Stage 8

```text
Issue type classifier
Document impact model
```

## Stage 9

```text
RFI summarisation
Embeddings
Semantic search
```

## Stage 10

```text
RFI Copilot
AI evaluation
Responsible AI
```

## Stage 11

```text
Optional FastAPI
Optional SharePoint integration
Portfolio polish
```

---

# 55. Minimum Viable Project

If time is limited, finish:

```text
Real RFI dataset
Python cleaning
SQL
Power BI
Databricks
Discipline classification
RFI summarisation
```

This is already a strong Digital Engineering portfolio project.

---

# 56. Strong Portfolio Version

For the strongest version, complete:

```text
Python ETL
PostgreSQL
Power BI
Databricks
Delta Lake
Discipline classification
Issue classification
Document impact prediction
MLflow
Model Registry
Summarisation
Embeddings
Semantic search
RFI Copilot
AI evaluation
FastAPI
SharePoint / Graph integration
```

---

# 57. GitHub README Story

Use a summary like:

> Built an end-to-end Digital Engineering RFI Analytics & AI Platform using a real USACE construction RFI log. Developed Python pipelines to clean and standardise engineering queries, modelled RFI data in SQL, and created Power BI dashboards for engineering and document-control reporting. Extended the platform in Databricks with NLP models for discipline and issue classification, document-impact prediction, RFI summarisation, semantic search and an AI Copilot. Used MLflow for experiment tracking and model governance, with evaluation and responsible-AI controls.

---

# 58. Recruiter Talking Points

Focus on:

```text
Digital Engineering
Project systems
RFI workflow
Automation
Python
SQL
Power BI
APIs
Databricks
AI
System integration
Data governance
```

Example interview explanation:

> I started with a real USACE RFI workbook rather than a synthetic dataset. I built a Python pipeline to clean and structure the RFI data, loaded it into SQL and created a Power BI dashboard for project reporting. I then extended the project in Databricks by training NLP models to classify engineering disciplines and issue types, predict document impacts and generate concise RFI summaries. Finally, I added semantic search and an AI assistant for querying project RFIs in natural language.

---

# 59. Skills Demonstrated

## Digital Engineering

```text
RFI management
CDE concepts
Document control
Project workflows
Engineering metadata
```

## Data Engineering

```text
Python
ETL
SQL
Data quality
Databricks
Delta Lake
```

## Analytics

```text
Power BI
DAX
RFI KPIs
Engineering trends
Document impact analysis
```

## Machine Learning

```text
NLP
Classification
Feature engineering
MLflow
Model Registry
Evaluation
```

## Generative AI

```text
Summarisation
Embeddings
Semantic search
RAG
AI agents
Grounded Q&A
Evaluation
Guardrails
```

---

# 60. Project Completion Criteria

The project is complete when:

```text
✓ Raw workbook preserved
✓ Clean RFI dataset generated
✓ Engineering labels created
✓ SQL database created
✓ Power BI dashboard completed
✓ Databricks pipeline working
✓ Discipline classification implemented
✓ Issue classification implemented
✓ Document impact model implemented
✓ MLflow experiments tracked
✓ Model registered
✓ RFI summaries generated
✓ Semantic search working
✓ Copilot answers grounded questions
✓ AI evaluation documented
✓ README completed
✓ Architecture diagram completed
```

---

# 61. First Task to Start Now

Start with:

```text
01_raw_data_profiling.py
```

The script should:

```text
1. Open the uploaded Excel workbook
2. Identify the real header row
3. Read all RFI records
4. Standardise column names
5. Count total RFIs
6. Check missing values
7. Check duplicate RFI IDs
8. Profile question lengths
9. Profile response completeness
10. Export a clean profiling summary
```

Then move to:

```text
02_clean_rfi.py
```

Do not begin Power BI or Databricks before the cleaned RFI table exists.

That cleaned table is the foundation of the entire project.
