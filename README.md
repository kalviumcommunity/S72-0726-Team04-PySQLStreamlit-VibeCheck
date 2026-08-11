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

### 1. Prerequisites
Ensure you have Python 3.10+ and Node.js 18+ installed on your system.

### 2. Environment Variables
Check that the `.env` file in the root directory contains your Supabase secrets:
```
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```
*(Note: If these are not provided, the Django backend will safely fallback to using the CSV files located in `data/`.)*

### 3. Start the Backend (Django)
Open a terminal and run the following commands to start the API:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt # (or pip install django djangorestframework django-cors-headers supabase pandas)
python manage.py runserver
```

### 4. Start the Frontend (Next.js)
Open a separate terminal and run the following commands to start the UI:
```bash
cd frontend
npm install
npm run dev
```

Open your browser at `http://localhost:3000` to view the modern dashboard.

---

## 🛠️ Project Structure

```
S72-0726-Team04-PySQLStreamlit-VibeCheck/
├── .env                     # Environment variables for Supabase
├── backend/                 # Django DRF backend
│   ├── api/                 # Django app containing views processing Pandas/Supabase data
│   └── config/              # Django project settings (CORS config)
├── frontend/                # Next.js 14 frontend
│   ├── src/app/             # App router pages (dashboard layout)
│   ├── src/components/ui/   # Shadcn UI components
│   └── src/lib/             # API utility functions
└── data/                    # Datasets (used as local fallback if Supabase is offline)
    ├── employees.csv
    ├── onboarding.csv
    ├── support_tickets.csv
    └── tool_usage.csv
```
