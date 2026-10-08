# Power BI Dashboard 2 — Design & Document Impact

## 1. Dashboard Purpose

The **Design & Document Impact** dashboard evaluates how RFIs affect controlled construction documentation, with a specific focus on drawing and specification changes.

Its purpose is to help project managers, design coordinators, engineers, and document-control teams understand:

- how many RFIs require formal document updates,
- whether those updates affect drawings, specifications, or both,
- which disciplines generate the highest document-impact rates,
- which issue types are most strongly associated with design/document changes,
- and where unclassified or unknown document-impact records remain.

The dashboard extends the Executive Overview by moving from general RFI workload to the downstream design consequences of those RFIs.

---

## 2. Executive KPIs

The top row contains five key document-impact metrics:

| KPI | Value | Meaning |
|---|---:|---|
| Document Update RFIs | 19 | RFIs identified as requiring a controlled document update |
| Drawing Update RFIs | 18 | RFIs requiring a drawing update |
| Specification Update RFIs | 17 | RFIs requiring a specification update |
| Both Updates RFIs | 16 | RFIs requiring both drawing and specification updates |
| Document Update Rate | 17.76% | Share of all RFIs requiring a document update |

The drawing and specification update counts overlap because many RFIs affect both document types.

---

## 3. RFIs by Document Impact

### Visual: Horizontal Bar Chart

This visual divides all 107 RFIs into five document-impact categories:

| Document Impact | RFIs | Share |
|---|---:|---:|
| No update | 51 | 47.66% |
| Unknown | 37 | 34.58% |
| Both | 16 | 14.95% |
| Drawing only | 2 | 1.87% |
| Specification only | 1 | 0.93% |

The chart provides the clearest overall view of how RFIs affect project documentation.

Among the 19 RFIs that require an update:

- **16 (84.21%)** affect both drawings and specifications,
- **2 (10.53%)** affect drawings only,
- **1 (5.26%)** affects specifications only.

This indicates that when an RFI does trigger a formal document change, it usually has a combined impact across both drawings and specifications rather than affecting only one document type.

---

## 4. Document Impact by Issue Type

### Visual: 100% Stacked Bar Chart

This visual compares the document-impact composition of each RFI issue type.

Key patterns include:

- **Specification Clarification:** 14 RFIs require both drawing and specification updates, representing **22.58%** of all Specification Clarification RFIs.
- **Drawing Conflict:** 50% require updates to both drawings and specifications, although the category contains only two RFIs.
- **Missing Information:** 1 RFI requires both updates and 2 require drawing-only updates.
- **Compliance Requirement:** 72.73% remain classified as Unknown document impact.
- **Inspection / Quality:** 66.67% remain Unknown.
- **Scope Gap:** the single RFI in this category has Unknown document impact.
- **Constructability** and **Interface Coordination:** all RFIs are currently classified as requiring no document update.

This view helps distinguish issue categories that mainly generate clarification activity from those that are more likely to cause controlled design changes.

---

## 5. Document Impact by Discipline

### Visual: 100% Stacked Bar Chart

This chart shows the mix of document-impact outcomes within each technical discipline.

Important observations include:

- **Architectural:** 2 of 3 RFIs require both drawing and specification updates.
- **Civil:** 3 of 9 RFIs require both updates, while 6 require no update.
- **Electrical:** 8 RFIs require both updates, 2 require drawing-only updates, 1 requires a specification-only update, 27 require no update, and 2 remain Unknown.
- **General:** only 1 of 15 RFIs requires a document update, while 8 remain Unknown.
- **Other:** 23 of 24 RFIs remain Unknown.
- **Quality / Inspection:** all 3 RFIs remain Unknown.
- **Controls / SCADA:** both RFIs require no document update.
- **Cybersecurity:** one RFI requires no update and one remains Unknown.

The chart demonstrates why absolute RFI volume and design impact should be evaluated separately. A high-volume discipline is not necessarily the discipline with the highest update rate.

---

## 6. Document Update Rate by Discipline

### Visual: Horizontal Bar Chart

This visual compares the percentage of RFIs within each discipline that require document updates.

| Discipline | Total RFIs | Document Updates | Update Rate |
|---|---:|---:|---:|
| Architectural | 3 | 2 | 66.67% |
| Civil | 9 | 3 | 33.33% |
| Electrical | 40 | 11 | 27.50% |
| Mechanical | 4 | 1 | 25.00% |
| Structural | 5 | 1 | 20.00% |
| General | 15 | 1 | 6.67% |
| Controls / SCADA | 2 | 0 | 0.00% |
| Cybersecurity | 2 | 0 | 0.00% |
| Other | 24 | 0 | 0.00% |
| Quality / Inspection | 3 | 0 | 0.00% |

**Architectural has the highest update rate at 66.67%, but this is based on only three RFIs.**

**Electrical has the largest absolute number of document updates, with 11 RFIs requiring changes**, making it the most significant discipline in terms of total design-change workload.

---

## 7. Discipline Impact Matrix

### Visual: Matrix

The matrix provides a detailed comparison by discipline using:

- Total RFIs
- Document Update RFIs
- Drawing Conflict RFIs
- Specification Issue RFIs
- Document Update Rate

The current results show:

| Discipline | Total RFIs | Document Update RFIs | Drawing Conflict RFIs | Specification Issue RFIs | Document Update Rate |
|---|---:|---:|---:|---:|---:|
| Architectural | 3 | 2 | 0 | 3 | 66.67% |
| Civil | 9 | 3 | 1 | 6 | 33.33% |
| Controls / SCADA | 2 | 0 | 0 | 0 | 0.00% |
| Cybersecurity | 2 | 0 | 0 | 0 | 0.00% |
| Electrical | 40 | 11 | 1 | 24 | 27.50% |
| General | 15 | 1 | 0 | 13 | 6.67% |
| Mechanical | 4 | 1 | 0 | 4 | 25.00% |
| Other | 24 | 0 | 0 | 8 | 0.00% |
| Quality / Inspection | 3 | 0 | 0 | 0 | 0.00% |
| Structural | 5 | 1 | 0 | 4 | 20.00% |
| **Total** | **107** | **19** | **2** | **62** | **17.76%** |

> **Note:** `Specification Issue RFIs` represents RFIs whose issue type is **Specification Clarification**. It is different from `Spec Update RFIs`, which counts RFIs requiring an actual specification document update.

---

# Key Findings

## 1. Only 17.76% of all RFIs require formal document updates

Out of 107 RFIs, **19 require a document update**.

This suggests that most RFIs are clarification or coordination activities rather than events that result in formal document revision.

---

## 2. Document-changing RFIs usually affect both drawings and specifications

Of the 19 RFIs requiring updates:

- 16 affect both drawings and specifications,
- 2 affect drawings only,
- 1 affects specifications only.

Therefore, **84.21% of document-changing RFIs affect both document types**.

This indicates that most design-changing RFIs have a broader downstream documentation impact rather than an isolated drawing or specification consequence.

---

## 3. Electrical creates the greatest absolute document-change workload

Electrical contains:

- **40 total RFIs**
- **11 document update RFIs**
- **27.50% document update rate**

Although Architectural has the highest percentage update rate, Electrical generates substantially more total updates and therefore represents the largest absolute design-change workload.

---

## 4. Architectural has the highest document update rate, but on a small sample

Architectural has:

- 3 total RFIs,
- 2 document updates,
- a **66.67% update rate**.

This is the highest rate among all disciplines, but it should be interpreted cautiously because it is based on only three RFIs.

The dashboard therefore highlights the importance of comparing **absolute volume and percentage rate together**.

---

## 5. Civil also shows meaningful design-change exposure

Civil has:

- 9 RFIs,
- 3 document updates,
- a **33.33% update rate**.

This gives Civil the second-highest update rate among disciplines with recorded document changes.

---

## 6. Specification Clarification is the dominant design-related issue

There are **62 Specification Clarification RFIs**, representing the largest issue category in the dataset.

Within this category:

- 14 require both drawing and specification updates,
- 1 requires a specification-only update,
- 30 require no update,
- 17 remain Unknown.

This shows that specification questions are not only the largest source of RFIs, but also a significant source of formal design-document changes.

---

## 7. Unknown document impact is a major data-quality issue

**37 RFIs, or 34.58% of the total dataset, have Unknown document impact.**

This significantly limits the certainty of impact analysis.

The problem is particularly concentrated in:

- Other: 23 of 24 RFIs Unknown,
- General: 8 of 15 Unknown,
- Quality / Inspection: 3 of 3 Unknown,
- Compliance Requirement: 8 of 11 Unknown,
- Inspection / Quality issue type: 4 of 6 Unknown.

This should be treated as a data-quality or classification backlog rather than interpreted as evidence that those RFIs had no project impact.

---

## 8. Drawing Conflict is rare but potentially impactful

Only **2 RFIs** are classified as Drawing Conflict.

Of those:

- 1 requires both drawing and specification updates,
- 1 requires no document update.

The sample is too small for a broad conclusion, but it demonstrates that drawing-conflict RFIs can translate directly into formal design changes.

---

## 9. High RFI volume does not automatically mean high document-impact rate

The dashboard reveals an important distinction:

- **Electrical:** high volume and meaningful update rate
- **Other:** high volume but no currently confirmed document updates, with most records Unknown
- **Architectural:** very low volume but very high update rate
- **General:** moderate volume but low confirmed update rate

This means project teams should not prioritize disciplines using RFI counts alone. Both **volume** and **document-change intensity** should be considered.

---

# Management Interpretation

The dashboard indicates that the project's RFI process is primarily clarification-driven, but a smaller subset of RFIs has meaningful downstream design consequences.

The most significant confirmed design-change workload is concentrated in **Electrical**, while **Architectural and Civil show higher proportional update rates**. Specification Clarification is the dominant issue type and is also responsible for most document-changing RFIs.

At the same time, the high proportion of **Unknown document-impact records (34.58%)** means that the current analysis may understate the true level of design impact. Improving classification completeness would materially improve the reliability of future design-change analysis.

---

# Role Within the Power BI Solution

This dashboard is the second page in the broader construction RFI analytics solution:

1. **Executive Overview** — overall RFI health, trends, workload, and response performance
2. **Design & Document Impact** — drawing and specification consequences
3. **Coordination & Responsibility** — originating and responsible parties
4. **RFI Register** — searchable operational RFI records
5. **RFI Detail** — drill-through view of individual RFIs

The reporting flow is designed to move from:

**What is happening? → What impact is it having? → Who is involved? → Which RFI caused it?**

---

# Portfolio Description

> Developed a Power BI Design & Document Impact dashboard for construction RFI analytics, measuring drawing and specification changes across disciplines and issue types. The dashboard combines absolute RFI volumes with document-update rates to distinguish high-volume coordination activity from RFIs with direct design consequences, while also identifying data-quality gaps in document-impact classification.
