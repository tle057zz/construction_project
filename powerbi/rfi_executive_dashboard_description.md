# Power BI Dashboard Description — RFI Executive Overview

## 1. Dashboard Purpose

The **RFI Executive Overview** dashboard provides a high-level view of Request for Information (RFI) activity for a construction project. It is designed to help project managers, design coordinators, engineers, and other stakeholders quickly understand the current RFI workload, response performance, document impact, major technical disciplines, issue categories, and originating parties.

The dashboard uses an interactive Power BI layout so users can move from overall project health to more focused analysis by discipline, issue type, and RFI status.

---

## 2. Executive KPIs

The top section contains the main project-level RFI indicators:

| KPI | Current Value | Purpose |
|---|---:|---|
| Total RFIs | 107 | Total number of RFIs recorded in the dataset |
| Open RFIs | 8 | Number of RFIs that remain unresolved |
| Answered RFIs | 99 | Number of RFIs that have received a response |
| Response Rate | 92.52% | Percentage of all RFIs that have been answered |
| Document Update RFIs | 19 | Number of RFIs that require a drawing and/or specification update |

These KPIs provide an immediate summary of the overall RFI workload and project response performance.

---

## 3. Interactive Filters

Three slicers are positioned on the left side of the dashboard:

- **Discipline**
- **Issue Type**
- **Status**

The slicers allow users to narrow the report to a specific technical discipline, RFI issue category, or response status.

Selections dynamically update the KPI cards and all supporting visuals on the page.

---

## 4. RFI Trend and Response Performance

### Visual: Line Chart

**Title:** `Total RFIs and Response Rate`

The main time-series visual compares:

- **Total RFIs**
- **Response Rate**

over the RFI submission period.

The chart uses the project date dimension to show activity chronologically and allows the user to see:

- periods of high RFI submission volume,
- changes in response performance,
- dates where unresolved RFIs temporarily reduce the response rate,
- how the project team responds to peaks in RFI activity.

This visual provides the temporal context behind the summary KPI values.

---

## 5. Document Impact

### Visual: Donut Chart

**Title:** `Total RFIs by Document Impact`

The donut chart classifies RFIs according to whether they resulted in changes to construction documents.

Current categories include:

| Document Impact | RFIs |
|---|---:|
| No update | 51 |
| Unknown | 37 |
| Both drawing and specification | 16 |
| Drawing only | 2 |
| Specification only | 1 |

This visual distinguishes routine clarification RFIs from RFIs that result in formal drawing or specification changes.

A notable data-quality observation is that **37 RFIs currently have an unknown document impact**, representing a significant portion of the dataset and an opportunity for further classification.

---

## 6. RFIs by Discipline

### Visual: Horizontal Bar Chart

**Title:** `RFIs by Discipline`

The discipline visual shows which technical areas generate the greatest RFI workload.

Current distribution includes:

- Electrical — 40
- Other — 24
- General — 15
- Civil — 9
- Structural — 5
- Mechanical — 4
- Architectural — 3
- Quality / Inspection — 3
- Controls / SCADA — 2
- Cybersecurity — 2

The chart is sorted in descending order so that the most active disciplines are immediately visible.

The current dataset shows that **Electrical is the dominant discipline**, accounting for the largest share of project RFIs.

---

## 7. RFIs by Issue Type

### Visual: Horizontal Bar Chart

**Title:** `Total RFIs by Issue Type`

This visual identifies the most common reasons RFIs are being raised.

Current issue categories include:

- Specification Clarification — 62
- Compliance Requirement — 11
- Missing Information — 11
- Design Clarification — 6
- Inspection / Quality — 6
- Material Requirement — 4
- Interface Coordination — 3
- Drawing Conflict — 2
- Constructability — 1
- Scope Gap — 1

The most important insight is that **Specification Clarification represents approximately 58% of all RFIs**, indicating that specification interpretation is the major source of information requests in the project.

---

## 8. RFIs by Originating Party

### Visual: Horizontal Bar Chart

**Title:** `Total RFIs by Party`

This visual shows which project organizations are submitting RFIs.

Current values include:

- DAVID BOLAND, INC — 71
- Carbon Recall Chattanooga — 11
- Dobco, Inc. — 8
- Richard Group LCC — 8
- Willdan — 8
- Schweitzer Engineering Laboratories, Inc. — 1

The chart helps identify where coordination demand is originating.

The current dataset shows that **DAVID BOLAND, INC accounts for roughly two-thirds of all RFIs**, making it the dominant originating party.

---

## 9. Dashboard Interaction

The report is designed to support cross-filtering.

For example, selecting **Electrical** in the discipline chart can filter:

- KPI cards,
- the RFI trend,
- document impact,
- issue types,
- originating parties.

Likewise, selecting an issue type or party can update the rest of the dashboard to show only the relevant subset of RFIs.

This allows users to move from an executive-level overview into focused analysis without leaving the page.

---

## 10. Executive Interpretation

At the current reporting point:

> The project contains **107 RFIs**, of which **99 have been answered and 8 remain open**, resulting in a **92.52% response rate**. Electrical is the most active technical discipline, while Specification Clarification is the dominant issue type. Nineteen RFIs have resulted in document updates, showing that a meaningful portion of the RFI workload has a direct impact on controlled project documentation.

The dashboard therefore provides visibility into both **RFI workload** and **design-coordination impact**, rather than simply reporting raw counts.

---

## 11. Role Within the Wider Power BI Solution

This dashboard is intended to act as the first page of a broader construction RFI analytics solution.

The planned reporting structure is:

1. **Executive Overview** — overall RFI health and project trends
2. **Design & Document Impact** — drawing and specification consequences
3. **Coordination & Responsibility** — originating and responsible parties
4. **RFI Register** — searchable operational RFI records
5. **RFI Detail** — drill-through view of individual questions, responses, notes, and document impact

Together, these pages allow users to move from high-level project performance to detailed investigation of individual RFIs.

---

## 12. Portfolio Description

A concise portfolio description for this page is:

> Developed an interactive Power BI Executive RFI Dashboard for a construction project using a dimensional star schema. The report provides visibility into RFI volume, open and answered queries, response performance, discipline and issue concentration, document impact, and stakeholder activity, with interactive filtering and cross-highlighting to support project and design coordination.
