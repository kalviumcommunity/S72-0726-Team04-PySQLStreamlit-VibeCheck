# Operational Data & Onboarding Analytics Datasets

This folder contains the core employee dataset and synthetic operational datasets for the **S72-0726-Team04-PySQLStreamlit-VibeCheck** sprint project.

## Problem Context
> *"A rapidly scaling startup stores employee onboarding progress, internal tool usage, and support request history separately, but leadership has no visibility into which operational friction points slow down new hire productivity during their first month."*

To model this scenario, we combine the real-world **IBM HR Analytics Employee Attrition** dataset with three realistically synthesized operational datasets to enable SQL queries, ETL transformations, and Streamlit dashboard analytics.

---

## Datasets Overview & Summary Statistics

| Dataset File | Source / Type | Primary Key | Foreign Keys | Row Count | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [`employees.csv`](file:///c:/Users/v4paw/Desktop/VIBE/S72-0726-Team04-PySQLStreamlit-VibeCheck/data/employees.csv) | IBM HR (Kaggle) | `employee_id` | None | **1,470** | Master employee demographic, department, role, and salary data. |
| [`onboarding.csv`](file:///c:/Users/v4paw/Desktop/VIBE/S72-0726-Team04-PySQLStreamlit-VibeCheck/data/onboarding.csv) | Synthetic (1:1) | `employee_id` | `employee_id` → `employees.employee_id` | **1,470** | Tracked onboarding checklists, training completion %, days, and status. |
| [`tool_usage.csv`](file:///c:/Users/v4paw/Desktop/VIBE/S72-0726-Team04-PySQLStreamlit-VibeCheck/data/tool_usage.csv) | Synthetic (1:N) | `usage_id` | `employee_id` → `employees.employee_id` | **~7,800** | Daily tool activity logs (Slack, Jira, GitHub, VS Code, Notion, etc.). |
| [`support_tickets.csv`](file:///c:/Users/v4paw/Desktop/VIBE/S72-0726-Team04-PySQLStreamlit-VibeCheck/data/support_tickets.csv) | Synthetic (1:N) | `ticket_id` | `employee_id` → `employees.employee_id` | **~890** | Internal IT/DevOps support requests, priority, and resolution hours. |

---

## Entity-Relationship Model (ERD)

```
+------------------+         1 : 1         +-------------------------------+
|    EMPLOYEES     | --------------------> |          ONBOARDING           |
+------------------+                       +-------------------------------+
| PK  employee_id  |                       | PK,FK employee_id             |
|     Department   |                       |      orientation_completed    |
|     JobRole      |                       |      training_completion_pct  |
|     Gender       |                       |      onboarding_days          |
|     Age          |                       |      onboarding_status        |
|     Education    |                       |      manager_assigned         |
|     ...          |                       |      buddy_assigned           |
+------------------+                       |      onboarding_comp_date     |
    |          |                           +-------------------------------+
    |          |
    | 1 : N    | 1 : N
    v          v
+-----------------------+                +---------------------------------+
|      TOOL_USAGE       |                |         SUPPORT_TICKETS         |
+-----------------------+                +---------------------------------+
| PK  usage_id          |                | PK  ticket_id                   |
| FK  employee_id       |                | FK  employee_id                 |
|     date              |                |     created_date                |
|     tool_name         |                |     issue_type                  |
|     login_count       |                |     priority                    |
|     active_minutes    |                |     resolution_hours            |
|     feature_used      |                |     status                      |
|     device_type       |                |     assigned_team               |
+-----------------------+                +---------------------------------+
```

---

## Detailed Data Schemas

### 1. `employees.csv`
- **Source**: [IBM HR Analytics Employee Attrition Dataset (Kaggle)](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset)
- **Columns**:
  - `employee_id` (INTEGER, PK): Unique employee identifier (renamed from `EmployeeNumber`).
  - `Department` (TEXT): Employee department (`Research & Development`, `Sales`, `Human Resources`).
  - `JobRole` (TEXT): Specific job title (e.g., `Software Engineer`, `Sales Executive`).
  - `Gender` (TEXT): `Male` or `Female`.
  - `Age` (INTEGER): Age of employee (18–60).
  - `Education` (INTEGER): Education level scale (1–5).
  - `BusinessTravel` (TEXT): Frequency of travel (`Travel_Rarely`, `Travel_Frequently`, `Non-Travel`).
  - `YearsAtCompany` (INTEGER): Total tenure at company in years (0–40).
  - `JobLevel` (INTEGER): Organizational level (1–5).
  - `MonthlyIncome` (INTEGER): Monthly salary in USD.

### 2. `onboarding.csv`
- **Columns**:
  - `employee_id` (INTEGER, PK/FK): References `employees.employee_id`.
  - `orientation_completed` (TEXT): `Yes` or `No`.
  - `training_completion_percent` (FLOAT): Module completion percentage (0.0–100.0%).
  - `onboarding_days` (INTEGER): Duration in days taken/allocated for onboarding.
  - `onboarding_status` (TEXT): Status (`Completed`, `In Progress`, `Delayed`).
  - `manager_assigned` (TEXT): `Yes` or `No`.
  - `buddy_assigned` (TEXT): `Yes` or `No`.
  - `first_week_checkin` (TEXT): `Yes` or `No`.
  - `onboarding_completion_date` (TEXT, YYYY-MM-DD): Date of completion or empty if in progress.

### 3. `tool_usage.csv`
- **Columns**:
  - `usage_id` (TEXT, PK): Formatted ID (e.g., `USG-000001`).
  - `employee_id` (INTEGER, FK): References `employees.employee_id`.
  - `date` (TEXT, YYYY-MM-DD): Log date within recent 30-day window.
  - `tool_name` (TEXT): Software tool (`Slack`, `Jira`, `GitHub`, `Confluence`, `VS Code`, `Google Workspace`, `Notion`).
  - `login_count` (TEXT/INT): Daily login sessions count (1–18).
  - `active_minutes` (INTEGER): Total active time in minutes (10–360).
  - `feature_used` (TEXT): Specific feature interacted with (e.g., `Pull Request Review`, `Code Commit`, `Doc Collaboration`).
  - `device_type` (TEXT): Primary device (`MacBook Pro`, `Windows Laptop`, `Linux Workstation`, `Mobile (iOS)`).

### 4. `support_tickets.csv`
- **Columns**:
  - `ticket_id` (TEXT, PK): Formatted ticket ID (e.g., `TCK-10001`).
  - `employee_id` (INTEGER, FK): References `employees.employee_id`.
  - `created_date` (TEXT, YYYY-MM-DD): Date ticket was submitted.
  - `issue_type` (TEXT): Type of issue (`Laptop Setup`, `Email Setup`, `VPN Access`, `MFA Issue`, `Software Installation`, `GitHub Access`, `Password Reset`, `Network Connectivity`).
  - `priority` (TEXT): `Low`, `Medium`, `High`, `Critical`.
  - `resolution_hours` (FLOAT): Hours taken to resolve ticket (empty/NaN if still open).
  - `status` (TEXT): `Resolved`, `Closed`, `In Progress`, `Pending`.
  - `assigned_team` (TEXT): Resolving team (`IT Helpdesk`, `DevOps`, `SecOps`, `Infrastructure`).

---

## Business Rules & Generation Logic

1. **Onboarding Tenure Correlation**:
   - Employees with `YearsAtCompany == 0` or `1` represent recent hires; their onboarding completion dates are within recent months or currently `In Progress` / `Delayed`.
   - Tenured employees (`YearsAtCompany > 1`) have `Completed` status with historical completion dates.
2. **Training & Ticket Volume Correlation**:
   - Employees with lower training completion (< 60%) or recent hire status generate 2–4x more support tickets than high-completion employees.
   - Onboarding-specific issues (`Laptop Setup`, `Email Setup`, `VPN Access`, `MFA Issue`) concentrate among new hires.
3. **Ticket Priority & Resolution Time**:
   - `Critical` tickets average 24–72 resolution hours, while `Low` priority tickets resolve in 0.5–4 hours.
4. **Department Tool Patterns**:
   - `Research & Development` employees predominantly log activity in `VS Code`, `GitHub`, `Jira`, and `Slack` on `MacBook Pro` or `Linux Workstation`.
   - `Sales` employees heavily use `Google Workspace`, `Notion`, and `Slack`.
5. **Operational Friction on Tool Activity**:
   - Employees with unresolved critical tickets or low training completion show lower daily login counts and active minutes.

---

## How to Regenerate Datasets

To regenerate all datasets from scratch and run internal validation tests:

```bash
# Ensure dependencies are installed
pip install kagglehub pandas numpy

# Run generator script from project root
python generate_datasets.py
```

The script will automatically download the base dataset from Kaggle, clean it, generate all synthetic data, run 5 integrity validation assertions, and save updated CSV files in `data/`.
