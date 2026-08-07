# VibeCheck: Operational Data & Onboarding Analytics

[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![Supabase](https://img.shields.io/badge/Supabase-REST_API-3ECF8E?logo=supabase)](https://supabase.com)
[![SQL](https://img.shields.io/badge/PySQL-SQLite_In_Memory-003B57?logo=sqlite)](https://sqlite.org)
[![Design](https://img.shields.io/badge/Design_System-Mastercard_Editorial-CF4500)](#-design-system)

## Problem Context
> *"A rapidly scaling startup stores employee onboarding progress, internal tool usage, and support request history separately, but leadership has no visibility into which operational friction points slow down new hire productivity during their first month."*

**VibeCheck** addresses this problem by combining real-world IBM HR Analytics data with interconnected operational datasets (onboarding checklists, support tickets, daily tool usage) into an interactive analytics dashboard, PySQL query engine, and Mastercard-inspired editorial interface.

---

## 🎨 Design System

VibeCheck is built following an **editorial magazine aesthetic** inspired by Mastercard:
- **Canvas Cream Palette (`#F3F0EE`)**: Warm putty background canvas replacing generic dark/white modes.
- **Stadium & Pill Forms**: `40px` radius hero media frames, `20px` radius card containers, and `999px` floating navigation pills.
- **Department Orbits**: Circular department cards with embedded vector SVG icons and satellite micro-CTAs.
- **Typographic Hierarchy**: `Sofia Sans` display typography with tight negative letter-spacing and Signal Orange (`#CF4500`) eyebrow accents.
- **Icon Integrity**: Pure SVG vector icons with zero emoji noise.

---

## 🏗️ Architecture & Datasets

```
+------------------+         1 : 1         +-------------------------------+
|    EMPLOYEES     | --------------------> |          ONBOARDING           |
+------------------+                       +-------------------------------+
| PK  employee_id  |                       | PK,FK employee_id             |
|     Department   |                       |      orientation_completed    |
|     JobRole      |                       |      training_completion_pct  |
|     ...          |                       |      onboarding_days          |
+------------------+                       |      onboarding_status        |
    |          |                           +-------------------------------+
    | 1 : N    | 1 : N
    v          v
+-----------------------+                +---------------------------------+
|      TOOL_USAGE       |                |         SUPPORT_TICKETS         |
+-----------------------+                +---------------------------------+
| PK  usage_id          |                | PK  ticket_id                   |
| FK  employee_id       |                | FK  employee_id                 |
|     tool_name         |                |     issue_type                  |
|     active_minutes    |                |     resolution_hours            |
+-----------------------+                +---------------------------------+
```

1. **`employees.csv`**: Master employee demographics, department, job role, and tenure.
2. **`onboarding.csv`**: Module completion percentages, days taken, manager & buddy assignments.
3. **`support_tickets.csv`**: Internal IT/DevOps support requests, priority, and resolution hours.
4. **`tool_usage.csv`**: Session activity logs across internal software tools (Slack, Jira, GitHub, VS Code, Notion, Google Workspace).

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Dependencies
Ensure Python 3.10+ is installed on your system:

```bash
pip install pandas numpy streamlit plotly kagglehub python-dotenv
```

### 2. Generate Datasets & SQL Schemas
Regenerate synthetic datasets, validate referential integrity, and compile standard ANSI `.sql` files:

```bash
# Generate datasets into data/
python generate_datasets.py

# Generate DDL & INSERT SQL scripts
python generate_sql.py
```

### 3. Sync to Supabase REST API (Optional)
Upload tables to Supabase with upsert handling (`resolution=merge-duplicates`). Configure credentials via `.env` or environment variables:

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"

python upload_rest.py
```

### 4. Launch Streamlit Web App
Run the interactive dashboard locally:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 📊 Dashboard Modules

- **Executive Overview**: High-level KPIs, department breakdown, ticket priority pie charts.
- **Onboarding Friction**: Scatter plot correlations between training completion %, support tickets generated, and high-friction employee directory.
- **IT Support Bottlenecks**: Resolution time distribution by priority and team workload bar charts.
- **Tool Adoption & Activity**: Tool active minutes distribution and login frequency analysis.
- **PySQL Sandbox**: In-memory SQLite console supporting multi-table ANSI SQL queries with instant execution and CSV export.

---

## 🛠️ Project Structure

```
S72-0726-Team04-PySQLStreamlit-VibeCheck/
├── app.py                   # Streamlit web application with Mastercard Design System
├── generate_datasets.py     # Dataset generation & integrity validation pipeline
├── generate_sql.py          # SQL DDL & INSERT statement generator
├── upload_rest.py           # Supabase REST API uploader with .env support
├── employees.sql            # Generated SQL schema & data for employees
├── onboarding.sql           # Generated SQL schema & data for onboarding
├── support_tickets.sql      # Generated SQL schema & data for support_tickets
├── tool_usage.sql           # Generated SQL schema & data for tool_usage
└── data/
    ├── README.md            # Data schema documentation & statistics
    ├── employees.csv        # Master employee dataset
    ├── onboarding.csv       # Onboarding checklist dataset
    ├── support_tickets.csv  # IT/DevOps tickets dataset
    └── tool_usage.csv       # Software tool activity dataset
```
