# VibeCheck: Operational Data & Onboarding Analytics

[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-API-092E20?logo=django)](https://www.djangoproject.com/)
[![Supabase](https://img.shields.io/badge/Supabase-REST_API-3ECF8E?logo=supabase)](https://supabase.com)

## 📌 About the Project

**VibeCheck** is an interactive analytics dashboard designed to give leadership visibility into operational friction points that slow down new hire productivity during their first month. 

By combining HR demographics, onboarding checklists, support tickets, and daily tool usage, VibeCheck helps identify bottlenecks and highlights employees who are struggling (experiencing high "friction").

---

## 📈 Understanding the Dashboard & Metrics

### What is the "Friction Score"?
The **Friction Score** is a composite metric indicating how difficult an employee's onboarding experience is. It is calculated by cross-referencing their **training completion percentage** against the **number of support tickets** they've raised. 
- A **high score ( > 70 )** indicates the employee is blocked, undertrained, or struggling with IT issues, requiring immediate intervention.
- A **low score** means smooth onboarding.

### What the Graphs Tell Us:
- **Friction Correlation (Scatter Plot)**: Shows the relationship between training completion and support tickets. Generally, employees with lower training completion raise more support tickets, indicating a clear operational bottleneck.
- **Tool Adoption Over Time (Line Chart)**: Tracks how quickly new hires adopt and actively use internal tools (like Jira, GitHub, or Slack) over their first weeks.
- **Top IT Bottlenecks (Bar Chart)**: Highlights the most common types of support tickets raised by new hires (e.g., access requests, hardware issues), identifying areas where IT can proactively remove blockers.
- **Buddy Impact (Bar Chart)**: Demonstrates the effectiveness of the onboarding buddy program by comparing the training completion rates of employees with and without an assigned buddy.

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
*(Note: If these are not provided, the Django backend will safely fallback to using the CSV files located in the `data/` folder.)*

### 3. Start the Backend (Django)
Open a terminal and run the following commands to start the API:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

### 4. Start the Frontend (Next.js)
Open a separate terminal and run the following commands to start the UI:
```bash
cd frontend
npm install
npm run dev
```

Open your browser at `http://localhost:3000` to view the dashboard!

---

## 🛠️ Project Structure

```
S72-0726-Team04-PySQLStreamlit-VibeCheck/
├── .env                     # Environment variables for Supabase
├── backend/                 # Django DRF backend API
│   ├── api/                 # Django app processing Pandas/Supabase data
│   └── config/              # Django project settings
├── frontend/                # Next.js frontend application
│   ├── src/app/             # App router pages (dashboard layout)
│   ├── src/components/      # UI components and Recharts charts
│   └── src/lib/             # API utility functions
└── data/                    # Datasets (used as local fallback)
```
