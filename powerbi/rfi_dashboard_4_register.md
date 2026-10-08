# Power BI Dashboard 4 — RFI Register

## 1. Dashboard Purpose

The **RFI Register** is the operational investigation page of the construction RFI analytics solution.

Unlike the first three dashboards, which focus on executive trends, design/document impact, and stakeholder responsibility, this page is designed for **record-level review**.

Its main purpose is to answer:

> **Which RFIs require review, follow-up, or document action?**

The dashboard allows users to search, filter, and inspect individual RFIs while retaining high-level context through summary KPI cards.

---

# 2. Role Within the Overall Power BI Solution

The reporting flow now consists of four complementary dashboards:

1. **Executive Overview**
   - What is happening across the project?
   - How many RFIs are open or answered?
   - Which disciplines and issue types dominate?

2. **Design & Document Impact**
   - Which RFIs affect drawings or specifications?
   - Which disciplines have the highest document-change exposure?

3. **RFI Origin, Assignment & Outstanding Workload**
   - Who generates RFIs?
   - Who is responsible for answering them?
   - Where is unresolved workload concentrated?

4. **RFI Register**
   - Which individual RFIs require investigation?
   - What are their status, discipline, issue type, parties, question summary, and document impact?

The analytical progression is therefore:

```text
Project Health
      ->
Design Impact
      ->
Stakeholder Responsibility
      ->
Individual RFI Investigation
```

---

# 3. Dashboard Structure

The page is intentionally **table-first rather than chart-heavy**.

This is appropriate because its primary purpose is operational investigation rather than high-level analytical comparison.

The dashboard consists of:

- search and filter controls,
- four summary KPI cards,
- and a detailed RFI register table.

This design maximises the amount of useful record-level information visible on a single page.

---

# 4. Page Header

The page heading communicates the operational purpose of the dashboard:

> **Search, Filter & Investigate Individual RFIs**

The supporting question is:

> *Which RFIs require review, follow-up, or document action?*

This distinguishes the page from the previous analytical dashboards and makes it clear that this is the investigation layer of the Power BI solution.

---

# 5. Summary KPI Cards

The top section includes four KPI cards:

| KPI | Current Value | Purpose |
|---|---:|---|
| Total RFIs | 107 | Number of RFIs in the current filter context |
| Open RFIs | 8 | Unresolved RFIs requiring follow-up |
| Response Rate | 92.52% | Percentage of RFIs that have been answered |
| Document Update RFIs | 19 | RFIs requiring a formal document update |

These cards are dynamic and respond to the dashboard filters.

For example, selecting a specific discipline, party, status, or document-impact category automatically recalculates the KPI values for the selected subset.

For an operational register, the `Total RFIs` card can also be renamed **Selected RFIs** because its value changes with filter context.

---

# 6. RFI ID Search

### Visual: Input Slicer

The RFI ID input slicer allows users to directly search for an individual record.

Field:

```text
fact_rfi[rfi_id]
```

This is particularly useful when the user already knows a specific RFI number and wants to locate the record immediately without manually scanning the register.

Example:

```text
RFI-008
```

---

# 7. Status Filter

### Visual: Button Slicer

The status filter contains:

```text
Answered
Open
```

This provides a fast way to isolate the unresolved RFI backlog.

For example:

```text
Status = Open
```

reduces the register to the eight currently unresolved RFIs.

This is one of the most important operational filters on the page.

---

# 8. Discipline Filter

### Visual: List Slicer

The discipline slicer allows users to investigate RFIs within a specific technical area.

Current disciplines include:

- Architectural
- Civil
- Controls / SCADA
- Cybersecurity
- Electrical
- General
- Mechanical
- Other
- Quality / Inspection
- Structural

This filter is useful when engineers or discipline leads need to review only the RFIs relevant to their area of responsibility.

---

# 9. Party Filter

The current dashboard includes a `party_name` slicer.

Because the Power BI model uses a single party dimension with different relationship roles, the slicer's meaning depends on the active relationship.

In the current model, the active relationship is based on:

```text
fact_rfi[from_party_key]
```

Therefore the existing `party_name` slicer represents the:

> **Originating Party**

For clarity, the visual title should therefore be changed from:

```text
party_name
```

to:

> **Originating Party**

If responsible-party filtering is required in the future, a separate slicer can be created using the explicit row-level `Responsible Party Name` field.

---

# 10. Document Impact Filter

### Visual: List Slicer

The document-impact filter contains:

- Both
- Drawing only
- No update
- Specification only
- Unknown

This allows users to quickly isolate RFIs with a potential downstream design/document-control consequence.

For example:

```text
Document Impact = Both
```

returns RFIs requiring changes to both drawings and specifications.

This is particularly useful for design coordination and document-control review.

---

# 11. RFI Register Table

The main visual is the detailed **RFI Register**.

The register currently contains the following fields:

- RFI ID
- Year
- Month
- Day
- Status
- Discipline
- Issue Type
- Originating Party
- Responsible Party
- Question Summary
- Document Impact

The table allows project users to move from high-level filtering to individual RFI investigation.

---

# 12. Recommended Register Column Structure

For a cleaner final version, the three separate date columns:

```text
Year
Month
Day
```

can be replaced with a single field:

```text
Received Date
```

formatted as:

```text
dd MMM yyyy
```

For example:

```text
04 Sep 2026
```

The recommended final register structure is:

| Column | Purpose |
|---|---|
| RFI | Unique RFI identifier |
| Received | Date the RFI was received |
| Status | Answered or Open |
| Discipline | Technical discipline |
| Issue Type | Type of problem or clarification |
| Originating Party | Organisation submitting the RFI |
| Responsible Party | Party tasked with responding |
| Document Impact | Drawing/specification consequence |
| Question Summary | Short preview of the RFI question |

This structure maximises readability while preserving all important project-control context.

---

# 13. Question Summary

The register uses a shortened question field rather than displaying the full RFI question.

This is important because full questions can be lengthy and would dramatically increase row height.

A preview field allows users to identify the subject of the RFI while keeping the register compact.

The full question remains available in the source data if deeper investigation is required.

---

# 14. Dashboard Interaction

The dashboard is designed so that filters work together.

For example, a user can select:

```text
Status = Open
Discipline = Electrical
Document Impact = Both
```

and the register will return only RFIs matching all three conditions.

The KPI cards also update automatically to describe the filtered subset.

Another useful workflow is:

```text
Originating Party
        +
Status = Open
        +
Document Impact
```

This allows project teams to identify which stakeholders are waiting for responses and whether those unresolved RFIs may require formal drawing or specification changes.

---

# 15. Operational Use Cases

The RFI Register can support several common project-control workflows.

## Open RFI Review

Filter:

```text
Status = Open
```

Purpose:

- review the current unresolved backlog,
- identify responsible parties,
- inspect technical disciplines,
- assess potential document impact.

## Discipline Review

Filter:

```text
Discipline = Electrical
```

Purpose:

- isolate all RFIs associated with the Electrical discipline,
- review unanswered queries,
- identify design/document consequences.

## Document-Control Review

Filter:

```text
Document Impact = Both
```

or:

```text
Drawing only
Specification only
```

Purpose:

- identify RFIs requiring formal drawing/specification changes,
- support design coordination and document-control follow-up.

## Individual RFI Search

Enter:

```text
RFI-XXX
```

into the RFI ID input slicer.

Purpose:

- immediately retrieve a known RFI,
- review its metadata and question summary,
- identify its responsible party and document impact.

---

# 16. Important Dashboard Findings

Dashboard 4 is primarily an operational register rather than a standalone analytical page, so its purpose is not to introduce many new aggregated findings.

However, it directly exposes the key project-control facts identified by the previous dashboards:

- **107 total RFIs**
- **99 answered RFIs**
- **8 open RFIs**
- **92.52% overall response rate**
- **19 RFIs requiring document updates**

It also provides the record-level evidence behind those metrics.

For example, the eight open RFIs identified at executive level can now be individually reviewed to determine:

- who submitted them,
- who is responsible for answering them,
- their technical discipline,
- their issue category,
- their question content,
- and whether they affect controlled project documentation.

This makes Dashboard 4 the bridge between analytical findings and operational follow-up.

---

# 17. Important Modelling Notes

## Party Roles

The dataset contains two different party roles:

```text
from_party_key
tasked_party_key
```

These represent:

- Originating Party
- Responsible Party

Because one `dim_party` table is used for both roles, care must be taken when configuring slicers and measures.

Explicit row-level fields for Originating Party Name and Responsible Party Name are useful for the RFI Register because they prevent role ambiguity.

## Date Presentation

For final presentation, a single Received Date field is preferable to separate Year, Month, and Day columns.

This reduces horizontal space requirements and improves readability.

## Response-Time Metrics

The current dataset does not contain a true RFI response/closure date.

Therefore the dashboard should not claim:

- average response time,
- days open,
- overdue status,
- closure duration,
- SLA compliance.

These would require additional source data.

---

# 18. Why the Dashboard Is Table-First

Dashboard 4 intentionally does not repeat the large analytical charts already used on the first three pages.

The report already provides:

- RFI trend analysis,
- discipline analysis,
- issue-type analysis,
- document-impact analysis,
- stakeholder workload analysis.

Repeating those visuals on the Register page would reduce space available for record-level investigation without adding substantial analytical value.

The table-first approach therefore improves:

- readability,
- operational usability,
- record-level investigation,
- and report-page efficiency.

---

# 19. Recommended Final Improvements

Before finalising the dashboard, the following presentation refinements are recommended:

1. Rename `party_name` to **Originating Party**.
2. Replace separate Year / Month / Day columns with **Received Date**.
3. Consider renaming `Total RFIs` KPI to **Selected RFIs**.
4. Format Response Rate as **92.5%** rather than 92.52%.
5. Apply conditional formatting to:
   - Open status,
   - document-impact categories,
   - Unknown document impact.
6. Keep Question Summary compact to minimise row height.

These changes are presentation improvements rather than changes to the analytical design.

---

# 20. Do We Need Dashboard 5?

## Recommendation: Dashboard 5 is optional, not required.

The Power BI solution is already complete and logically coherent with four dashboards.

The four-page structure provides:

```text
Dashboard 1
Executive Overview
        ↓
Dashboard 2
Design & Document Impact
        ↓
Dashboard 3
Coordination & Responsibility
        ↓
Dashboard 4
RFI Register
```

This already supports the full analytical flow from executive-level monitoring to individual RFI investigation.

For a portfolio project, stopping at Dashboard 4 is completely reasonable.

## When Dashboard 5 Would Add Value

A fifth **RFI Detail** page would only be necessary if the project aims to demonstrate additional Power BI functionality such as:

- drill-through,
- detailed record navigation,
- full-question display,
- full-response display,
- notes review,
- back-navigation buttons.

The fifth page would contain one selected RFI at a time and show:

```text
RFI ID
Received Date
Status
Discipline
Issue Type

Originating Party
Responsible Party

Full Question
Full Response
Notes

Drawing Update Required
Specification Update Required
Document Impact
```

This would demonstrate advanced Power BI interaction, but it would not introduce a new analytical layer.

---

# 21. Final Recommendation

For this project, the **four-dashboard solution is sufficient and well structured**.

Dashboard 5 should be treated as an optional enhancement rather than a requirement.

If the objective is to demonstrate:

- data modelling,
- DAX,
- project-control analytics,
- interactive filtering,
- construction-domain understanding,
- and practical Power BI dashboard design,

then Dashboards 1–4 already achieve that goal.

A fifth drill-through page can be added later if demonstrating advanced Power BI navigation becomes important, but the current solution can confidently end with the RFI Register.

---

# 22. Portfolio Description

> Developed an operational Power BI RFI Register that enables construction project teams to search, filter, and investigate individual RFIs by status, technical discipline, stakeholder, and document impact. The dashboard connects executive-level project metrics to record-level evidence, allowing users to identify unresolved queries, responsible parties, design-document consequences, and specific RFIs requiring follow-up.
