# HSEI Platform
### HSE Incident Analytics & Process Safety Intelligence

> Production-grade HSE analytics platform for Oil & Gas operations.
> Standards: API RP 754 · ISO 45001 · OSHA 29 CFR 1910.119 · RIDDOR

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)](https://streamlit.io)
[![Standard](https://img.shields.io/badge/Standard-API%20RP%20754-orange)](.)
[![Tests](https://img.shields.io/badge/Tests-29%20Passed-brightgreen)](.)

---

## Platform Overview

| Module | Coverage |
|---|---|
| Incident Register | TRIR, LTIR, severity tracking, cost analysis |
| Process Safety | API RP 754 Tier 1–4 classification and trending |
| Corrective Actions | Action close-out tracking, overdue management |
| Leading Indicators | Near miss ratio, Stop Work Authority, reporting culture |
| HSE Inspections | Score trending, findings analysis, audit performance |
| Permit to Work | Compliance monitoring, violation tracking |
| Training & Competency | Expiry tracking, compliance by department and course |

---

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/hsei-platform.git
cd hsei-platform
pip install -r requirements.txt
python scripts/setup_database.py
streamlit run dashboards/app.py
```

## Docker

```bash
docker-compose up -d
# http://localhost:8503
```

---

## Key KPIs

| KPI | Formula | Industry Target |
|---|---|---|
| TRIR | (Recordables × 200,000) / Manhours | ≤ 0.30 (world class) |
| LTIR | (LTIs × 200,000) / Manhours | ≤ 0.10 (world class) |
| Near Miss Ratio | Near Misses / Recordables | ≥ 5:1 |
| Action Close-out | Closed / Total × 100 | ≥ 85% |
| Training Compliance | Valid / Total × 100 | ≥ 95% |

---

## Database — 7 Tables

```
incidents           · hse_inspections    · training_records
corrective_actions  · permit_to_work     · kpi_monthly_summary
safety_observations
```

## Standards Alignment

- **API RP 754** — Process Safety Performance Indicators
- **ISO 45001** — Occupational Health & Safety Management
- **OSHA 29 CFR 1910.119** — Process Safety Management
- **RIDDOR** — Reporting of Injuries, Diseases and Dangerous Occurrences
- **NUPRC / NOSDRA** — Nigerian upstream regulatory framework

*HSEI Platform — Companion to ORPMI. Same facility, complete operational intelligence.*
