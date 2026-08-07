# ⚡ VibeCheck: Operational Data & Onboarding Analytics

[![Streamlit](https://img.shields.io/badge/Streamlit-1.61-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![Supabase](https://img.shields.io/badge/Supabase-REST_API-3ECF8E?logo=supabase)](https://supabase.com)
[![SQL](https://img.shields.io/badge/PySQL-SQLite_In_Memory-003B57?logo=sqlite)](https://sqlite.org)

## 📌 Problem Context
> *"A rapidly scaling startup stores employee onboarding progress, internal tool usage, and support request history separately, but leadership has no visibility into which operational friction points slow down new hire productivity during their first month."*

**VibeCheck** addresses this problem by combining real-world IBM HR Analytics data with interconnected operational datasets (onboarding checklists, support tickets, daily tool usage) into an interactive analytics dashboard and PySQL query engine.

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

1. **`employees.csv`**: Master employee demographics, department, job role, and salary.
2. **`onboarding.csv`**: Module completion percentages, days taken, manager & buddy assignments.
3. **`support_tickets.csv`**: Internal IT/DevOps support requests, priority, and resolution hours.
4. **`tool_usage.csv`**: Session activity logs across internal software tools (Slack, Jira, GitHub, VS Code, Notion, Google Workspace).

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Dependencies
Ensure Python 3.10+ is installed on your system.

```bash
pip install pandas numpy streamlit plotly kagglehub
```

### 2. Generate Datasets & SQL Schemas
Regenerate synthetic datasets, validate referential integrity, and compile standard ANSI `.sql` files:

```bash
# Generate datasets into data/
python generate_datasets.py

# Generate DDL & INSERT SQL scripts
python generate_sql.py
```

### 3. Sync to Supabase REST API
Upload tables to Supabase with upsert handling (`resolution=merge-duplicates`):

```bash
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

- **📊 Executive Overview**: High-level KPIs, onboarding completion rates, and department friction index.
- **⚡ Onboarding Friction**: Interactive correlation analysis between training completion %, support tickets generated, and days to onboard.
- **🎫 IT Support Bottlenecks**: Resolution time distribution by ticket priority and assigned team workload.
- **💻 Tool Adoption & Activity**: Tool session breakdown, active minutes, and device preferences.
- **🔍 PySQL Sandbox**: In-memory SQLite console allowing custom SQL queries (`SELECT`, `JOIN`, `GROUP BY`) with instant tabular view and CSV export.

---

## 🛠️ Project Structure

```
S72-0726-Team04-PySQLStreamlit-VibeCheck/
├── app.py                   # Main Streamlit web application & PySQL console
├── generate_datasets.py     # Dataset generation & validation pipeline
├── generate_sql.py          # SQL DDL & INSERT generator
├── upload_rest.py           # Supabase REST API uploader
├── employees.sql            # Generated SQL script for employees table
├── onboarding.sql           # Generated SQL script for onboarding table
├── support_tickets.sql      # Generated SQL script for support_tickets table
├── tool_usage.sql           # Generated SQL script for tool_usage table
└── data/
    ├── README.md            # Detailed schema documentation & data stats
    ├── employees.csv        # Master employee dataset
    ├── onboarding.csv       # Onboarding checklist dataset
    ├── support_tickets.csv  # IT/DevOps tickets dataset
    └── tool_usage.csv       # Software tool activity dataset
```
