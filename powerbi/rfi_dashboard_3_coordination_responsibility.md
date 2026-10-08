# Power BI Dashboard 3 — RFI Origin, Assignment & Outstanding Workload

## 1. Dashboard Purpose

The **RFI Origin, Assignment & Outstanding Workload** dashboard analyses stakeholder coordination across the construction RFI process.

Its main purpose is to answer three management questions:

1. **Who is generating RFIs?**
2. **Who is responsible for responding to them?**
3. **Where is the unresolved workload concentrated?**

The page complements the Executive Overview and Design & Document Impact dashboards by shifting the analysis from overall volume and design consequences to **stakeholder responsibility, workload ownership, response performance, and outstanding coordination demand**.

---

# 2. Important Data-Model Logic

The current Power BI model uses a single party dimension:

```text
dim_party[party_key]
```

The RFI fact table contains two party-related foreign keys:

```text
fact_rfi[from_party_key]
fact_rfi[tasked_party_key]
```

The active relationship is:

```text
dim_party[party_key]
        1
        |
        *
fact_rfi[from_party_key]
```

Therefore, standard measures such as:

```DAX
[Total RFIs]
[Open RFIs]
[Answered RFIs]
[Response Rate]
```

naturally analyse the **originating party**.

The relationship to:

```text
fact_rfi[tasked_party_key]
```

is inactive.

Responsible-party analysis therefore requires measures using:

```DAX
USERELATIONSHIP (
    dim_party[party_key],
    fact_rfi[tasked_party_key]
)
```

This distinction is critical because the same `dim_party[party_name]` field is used to represent two different stakeholder roles.

---

# 3. Dashboard KPIs

The top row contains the main coordination indicators:

| KPI | Current Value | Meaning |
|---|---:|---|
| Originating Parties | 6 | Number of organisations that submitted RFIs |
| Responsible Parties | 10 | Number of parties assigned responsibility for answering RFIs |
| Open RFIs | 8 | RFIs currently unresolved |
| Response Rate | 92.52% | Share of all RFIs that have been answered |
| Total RFIs | 107 | Total number of RFIs in the dataset |

These cards provide an immediate summary of stakeholder participation and overall response performance.

---

# 4. RFIs by Originating Party

### Visual: Column Chart

**Title:** `RFIs by Originating Party`

This visual shows which organisations generated the RFI workload.

Current distribution:

| Originating Party | Total RFIs |
|---|---:|
| DAVID BOLAND, INC | 71 |
| Carbon Recall Chattanooga | 11 |
| Dobco, Inc. | 8 |
| Richard Group LCC | 8 |
| Willdan | 8 |
| Schweitzer Engineering Laboratories, Inc. | 1 |

### Key Observation

**DAVID BOLAND, INC originated 71 of 107 RFIs, representing approximately 66.4% of the total RFI volume.**

This indicates that RFI generation is highly concentrated with one stakeholder.

---

# 5. Open RFIs by Originating Party

### Visual: Column Chart

This visual identifies which originating parties currently have unresolved RFIs.

Current open workload:

| Originating Party | Open RFIs |
|---|---:|
| Dobco, Inc. | 4 |
| Richard Group LCC | 3 |
| Willdan | 1 |

### Key Observation

Although DAVID BOLAND, INC originates the largest number of RFIs overall, it currently has **no open RFIs**.

The unresolved demand instead comes from:

- Dobco, Inc.
- Richard Group LCC
- Willdan

This demonstrates why **total RFI volume and current outstanding workload should not be interpreted as the same thing**.

---

# 6. RFIs by Responsible Party

### Visual: Column Chart

Responsible-party analysis uses the inactive `tasked_party_key` relationship through `USERELATIONSHIP()`.

Current assigned workload:

| Responsible Party | Assigned RFIs |
|---|---:|
| AE | 66 |
| CT | 15 |
| PM | 9 |
| JBMDL | 8 |
| AE/JBMDL | 4 |
| AE/JBMDL/PM | 1 |
| AE/PM | 1 |
| CT/PM | 1 |
| JBMDL/AE | 1 |
| USACE DB | 1 |

### Key Observation

**AE is responsible for 66 of 107 RFIs, approximately 61.7% of the total assignment workload.**

However, the party with the largest total assigned workload is not the party with the largest unresolved workload.

---

# 7. Response Rate by Responsible Party

### Visual: Column Chart

This visual compares response performance across the parties assigned to answer RFIs.

Current results:

| Responsible Party | Response Rate |
|---|---:|
| AE | 100.00% |
| AE/JBMDL | 100.00% |
| AE/JBMDL/PM | 100.00% |
| AE/PM | 100.00% |
| CT/PM | 100.00% |
| JBMDL | 100.00% |
| JBMDL/AE | 100.00% |
| PM | 100.00% |
| USACE DB | 100.00% |
| CT | 46.67% |

### Key Observation

**CT is the clear performance exception.**

CT has:

- 15 assigned RFIs
- 7 answered RFIs
- 8 open RFIs
- 46.67% response rate

All other responsible-party categories currently show a 100% response rate.

This makes CT the primary coordination bottleneck in the current dataset.

---

# 8. Open RFIs by Responsible Party

### Visual: Horizontal Bar Chart

This visual shows where the unresolved response workload currently sits.

Current result:

| Responsible Party | Open RFIs |
|---|---:|
| CT | 8 |

### Key Observation

**All 8 open RFIs are assigned to CT.**

This is the most actionable finding on the dashboard.

Although AE carries the highest total workload, CT carries the entire unresolved workload.

This highlights why management attention should focus on **outstanding ownership**, not simply total workload volume.

---

# 9. Originating Party Performance Table

### Visual: Table

The bottom-left table compares originating-party performance using:

- Total RFIs
- Answered RFIs
- Open RFIs
- Response Rate
- Document Update Rate

Current results include:

| Originating Party | Total RFIs | Answered | Open | Response Rate | Document Update Rate |
|---|---:|---:|---:|---:|---:|
| Dobco, Inc. | 8 | 4 | 4 | 50.00% | 0.00% |
| Schweitzer Engineering Laboratories, Inc. | 1 | 1 | 0 | 100.00% | 0.00% |
| Richard Group LCC | 8 | 5 | 3 | 62.50% | 12.50% |
| Willdan | 8 | 7 | 1 | 87.50% | 12.50% |
| Carbon Recall Chattanooga | 11 | 11 | 0 | 100.00% | 18.18% |
| DAVID BOLAND, INC | 71 | 71 | 0 | 100.00% | 21.13% |
| **Total** | **107** | **99** | **8** | **92.52%** | **17.76%** |

### Important Interpretation

This table represents **originating-party performance**, because it uses the active `from_party_key` relationship.

It should not be interpreted as responsible-party response performance.

The table is most useful for identifying:

- which organisations currently have unanswered RFIs,
- their response completion level,
- and whether their RFIs are associated with document changes.

---

# 10. Assigned RFI Workload by Discipline

### Visual: 100% Stacked Bar Chart

This visual combines:

```text
Responsible Party
+
Discipline
```

to show the composition of each responsible party's assigned workload.

It uses:

```text
Y-axis:
dim_party[party_name]

Values:
[RFIs by Responsible Party]

Legend:
dim_discipline[discipline_name]
```

### Key Patterns

Important workload patterns include:

- **AE:** the majority of its assigned RFIs are Electrical.
- **CT:** 100% of its assigned RFIs are classified under the `Other` discipline.
- **PM:** most of its assigned workload is also concentrated in `Other`.
- **JBMDL:** the majority of its assigned workload is General.
- Smaller combined-responsibility groups have highly concentrated discipline mixes due to very small sample sizes.

### Why This Visual Matters

The normal Responsible Party chart answers:

> How much workload does each party have?

The stacked discipline chart answers:

> What type of technical workload does each responsible party have?

This gives the page a stronger coordination and resource-allocation perspective.

---

# 11. Key Findings

## 11.1 RFI generation is highly concentrated

DAVID BOLAND, INC originated:

- 71 RFIs
- approximately 66.4% of the total dataset

This means the majority of information demand originates from a single stakeholder.

---

## 11.2 Assigned responsibility is also highly concentrated

AE is responsible for:

- 66 RFIs
- approximately 61.7% of all assigned RFI workload

However, AE currently has no unresolved RFIs.

This demonstrates that **high workload volume does not automatically indicate poor response performance**.

---

## 11.3 The unresolved workload is completely concentrated with CT

CT has:

- 15 assigned RFIs
- 7 answered
- 8 open
- 46.67% response rate

All 8 open RFIs in the project are currently assigned to CT.

This makes CT the strongest candidate for immediate coordination follow-up.

---

## 11.4 Open demand comes from three originating parties

The eight unresolved RFIs originate from:

- Dobco, Inc. — 4
- Richard Group LCC — 3
- Willdan — 1

This means the current response bottleneck affects multiple external/internal stakeholders rather than a single originating organisation.

---

## 11.5 Total workload and unresolved workload tell different stories

The dashboard clearly separates:

- **who generates the most RFIs,**
- **who owns the most assignments,**
- and **who owns the current unresolved backlog.**

These are different management questions.

For example:

- DAVID BOLAND, INC generates the most RFIs.
- AE owns the most assigned workload.
- CT owns the entire open backlog.

This is the central analytical story of Dashboard 3.

---

## 11.6 Discipline mix provides context for assignment workload

Responsible-party workload composition varies significantly by discipline.

For example:

- AE's workload is dominated by Electrical RFIs.
- CT's workload is entirely classified as Other.
- JBMDL's assigned workload is predominantly General.

This may help explain differences in workload complexity, routing, or response responsibility.

---

# 12. Important Caveats and Modelling Notes

## 12.1 One party dimension is used for two roles

The model currently uses a single:

```text
dim_party
```

for both:

- originating party,
- responsible party.

Because only one relationship can be active at a time, responsible-party measures require `USERELATIONSHIP()`.

This is perfectly workable, but the report developer must be consistent about which relationship each measure uses.

---

## 12.2 Visual titles must clearly identify the party role

Because `dim_party[party_name]` is reused for both roles, visual titles should always explicitly state:

- **Originating Party**
- or **Responsible Party**

Avoid generic titles such as:

```text
RFIs by Party
```

because they are ambiguous.

---

## 12.3 Cross-filter interactions require care

When selecting a party in an originating-party visual, generic measures may follow the active originating-party relationship.

Responsible-party measures deliberately activate the tasked-party relationship.

For this reason, cross-filter behaviour between originating-party and responsible-party visuals should be tested carefully.

Where interactions produce confusing results, disable them using:

```text
Format -> Edit interactions
```

---

## 12.4 Response-time analysis is not currently available

The dataset includes RFI received dates but does not contain a true answered/closed date.

Therefore, this dashboard should not currently claim metrics such as:

- Average Response Days
- Days Open
- Overdue RFIs
- Average Closure Time
- Response SLA Compliance

Those metrics would require additional source data.

---

# 13. Recommended Final Visual Titles

Use the following titles for clarity:

1. **RFIs by Originating Party**
2. **Open RFIs by Originating Party**
3. **RFIs by Responsible Party**
4. **Response Rate by Responsible Party**
5. **Open RFIs by Responsible Party**
6. **Originating Party Performance**
7. **Assigned RFI Workload by Discipline**

The dashboard title should remain:

# RFI Origin, Assignment & Outstanding Workload

Subtitle / analytical question:

> Who is generating RFIs, who is responsible for responding, and where is unresolved workload concentrated?

---

# 14. Management Interpretation

The current RFI coordination picture is highly concentrated but in different places depending on the management question.

DAVID BOLAND, INC is the dominant originating party, generating approximately two-thirds of all RFIs. AE carries the largest assigned response workload, but has completed its current assigned responses.

The key operational concern is CT. All eight currently open RFIs are assigned to CT, leaving CT with a response rate of only 46.67%.

The outstanding RFIs originate from Dobco, Richard Group, and Willdan.

The dashboard therefore indicates that management attention should focus primarily on **CT's unresolved RFI queue**, rather than simply targeting the party with the highest overall assignment volume.

---

# 15. Role Within the Overall Power BI Solution

Dashboard 3 sits within the wider construction RFI analytics solution as follows:

1. **Executive Overview**
   - What is happening across the project?

2. **Design & Document Impact**
   - What design/document consequences are RFIs creating?

3. **RFI Origin, Assignment & Outstanding Workload**
   - Who is generating, owning, and delaying the RFI workload?

4. **RFI Register**
   - Which individual RFIs require investigation?

5. **RFI Detail**
   - What exactly happened within a specific RFI?

The analytical flow is therefore:

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

# 16. Portfolio Description

> Developed a Power BI stakeholder coordination dashboard for construction RFI management, separating RFI origin from assigned responsibility through relationship-aware DAX measures. The dashboard identifies stakeholder workload concentration, open RFI ownership, response-rate bottlenecks, and discipline-based assignment patterns, enabling project teams to distinguish high-volume stakeholders from the parties responsible for unresolved coordination issues.
