# Digital Engineering RFI Analytics & AI Platform
## Project Introduction and Data Source

# 1. Project Introduction

This project develops a **Digital Engineering RFI Analytics & AI Platform** using a real construction Request for Information (RFI) dataset from a U.S. Army Corps of Engineers infrastructure project.

The goal is to demonstrate how project information stored in spreadsheets and other semi-structured sources can be transformed into a structured digital workflow supporting project reporting, engineering coordination, document control, automation, and AI-assisted analysis.

The project architecture is:

```text
Raw RFI Excel Data
        ↓
Python Cleaning and Validation
        ↓
Structured SQL Database
        ↓
Power BI Reporting
        ↓
Databricks Analytics
        ↓
Machine Learning / NLP Models
        ↓
Semantic Search + RFI AI Copilot
```

The project is designed to demonstrate capability across:

- Digital Engineering
- RFI workflow management
- Project systems
- Engineering information management
- Python automation
- SQL and data modelling
- Power BI
- Databricks
- Machine learning
- Natural Language Processing
- Generative AI
- AI evaluation and governance

A major strength of the project is that it begins with a **real publicly released construction RFI register**, rather than a synthetic portfolio dataset.

# 2. Business Context

Construction and infrastructure projects generate large volumes of RFIs throughout design, procurement, and delivery.

RFIs are used when project participants need clarification regarding issues such as:

- unclear drawings
- conflicting specifications
- missing information
- constructability questions
- scope gaps
- coordination problems
- compliance questions
- material or equipment requirements

Because much of this information is stored as free text, it can be difficult to identify recurring engineering issues, document impacts, technical themes, or common clarification categories.

This project turns the RFI register into a structured analytical and AI-enabled platform.

# 3. Data Source

The dataset comes from the U.S. Army Corps of Engineers solicitation:

**Power Generation with Microgrid at Joint Base McGuire-Dix-Lakehurst (JBMDL), New Jersey**

Solicitation reference:

```text
W912DS26BA032
```

The project involves power-generation and microgrid infrastructure at Joint Base McGuire-Dix-Lakehurst in New Jersey.

The wider technical context includes:

- electrical generation
- battery energy storage
- solar photovoltaic systems
- SCADA and control systems
- cybersecurity
- civil works
- mechanical and utility systems
- specifications
- design drawings
- inspection requirements

# 4. Source File

The main source used in this project is:

```text
RFI log for posting 9.23.26.xlsx
```

The workbook was published as part of the public federal procurement opportunity and contains approximately **111 RFI records**.

The original workbook will be preserved unchanged as the raw project source.

# 5. Explore the Dataset

## Official SAM.gov Opportunity

Explore the official federal procurement opportunity here:

https://sam.gov/opp/2e4f861cc9dc4550bc3068d29d6363a9/view

From the **Attachments** section, look for:

```text
RFI log for posting 9.23.26.xlsx
```

## Public Dataset Preview / Mirror

A public indexed copy of the RFI workbook can also be explored here:

https://govtribe.com/file/government-file/w912ds26ba032-rfi-log-for-posting-9-dot-23-dot-26-dot-xlsx

# 6. Original Dataset Structure

The source workbook contains these main fields:

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

## RFI #

Identifier assigned to each Request for Information.

## FROM

Identifies the organisation or party that submitted the RFI.

Possible analysis:

```text
RFI count by submitting organisation
RFI topics by organisation
Most active submitting parties
```

## TASKED

Identifies the party or engineering function responsible for reviewing or responding to the RFI.

## DATE RECEIVED

The date on which the RFI was received.

This supports:

```text
RFI volume over time
Weekly RFI trends
Peak clarification periods
```

## QUESTION

The original engineering or technical question.

This is one of the most valuable fields because it contains unstructured engineering text.

Potential derived attributes include:

```text
engineering_discipline
issue_type
technical_topic
drawing_reference
specification_reference
equipment_reference
question_summary
```

## RESPONSE

The official answer or clarification associated with the RFI.

This supports:

```text
Question-response analysis
Technical resolution analysis
RFI summarisation
Semantic search
```

## NOTES

Contains supplementary information.

This field can help identify whether an RFI caused:

```text
Drawing update
Specification update
Attachment issue
Document revision
No document change
```

## Status

Represents the source status where populated.

The original source status will be preserved. If required, a separate derived status may be created, such as:

```text
Answered
Open
Unknown
```

# 7. Why This Dataset Is Suitable

This dataset is suitable because it combines:

- a real construction context
- structured project fields
- unstructured engineering text
- genuine RFI questions and responses
- relevant Digital Engineering and document-control use cases

The technical content supports classification across areas such as:

```text
Electrical
Mechanical
Civil
Structural
Controls / SCADA
Cybersecurity
Quality / Inspection
Specifications
Design Coordination
```

# 8. Planned Transformation

The project will maintain clear lineage between original source data and derived fields:

```text
Original Excel
      ↓
raw_rfi
      ↓
clean_rfi
      ↓
enriched_rfi
      ↓
SQL / Power BI
      ↓
Databricks ML + AI
```

## Raw Layer

```text
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

## Clean Layer

Standardises:

```text
RFI ID
Party names
Dates
Whitespace
Null values
Text encoding
Status
Duplicates
```

## Enriched Layer

Adds derived analytical and AI attributes:

```text
discipline
issue_type
technical_topic
reference_type
reference_number
drawing_update_required
spec_update_required
document_update_required
question_summary
response_available
classification_confidence
```

# 9. Data Limitations

The source contains approximately 111 RFIs, which is relatively small for supervised machine learning.

It also does not directly contain all fields expected in a mature RFI system, such as:

```text
Due Date
Response Date
Closed Date
Formal Priority
Cost Impact
Schedule Impact
Discipline
Issue Category
Workflow History
Revision History
```

Any additional fields derived using rules, manual labelling, or AI will be clearly marked as **derived attributes**.

The project will not present inferred values as if they were present in the original source.

# 10. Planned Use of the Dataset

## Python and SQL

```text
Data ingestion
Data cleaning
Validation
Transformation
Data modelling
```

## Power BI

```text
RFI overview
RFI trend analysis
RFI by discipline
RFI by issue type
Document impact analysis
Detailed RFI register
```

## Databricks and Machine Learning

```text
Discipline classification
Issue-type classification
Document-impact prediction
MLflow experiment tracking
Model Registry
```

## Generative AI

```text
RFI summarisation
Semantic search
RAG
Natural-language RFI querying
RFI AI Copilot
AI evaluation
```

# 11. Project Value

The final system demonstrates how a traditional RFI register can be converted into a modern Digital Engineering information platform.

> A real USACE RFI workbook is ingested and cleaned using Python, modelled in SQL, visualised through Power BI, and extended in Databricks with NLP classification, document-impact prediction, semantic search, and an AI Copilot for engineering information retrieval.

This connects:

```text
Construction
+
Digital Engineering
+
Project Systems
+
Data Analytics
+
Automation
+
AI
```
