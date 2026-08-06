"""
generate_datasets.py

Dataset Generation & Cleaning Pipeline for College Sprint Project:
S72-0726-Team04-PySQLStreamlit-VibeCheck

This script:
1. Downloads the IBM HR Analytics Employee Attrition dataset from Kaggle via kagglehub.
2. Cleans and extracts the core employee dataset (employees.csv).
3. Synthesizes three interconnected operational datasets:
   - onboarding.csv (1:1 with employees)
   - tool_usage.csv (1:N with employees, ~3500 rows)
   - support_tickets.csv (1:N with employees, ~1000 rows)
4. Validates referential integrity, row count constraints, and primary key uniqueness.
5. Saves all datasets as CSV files in the data/ folder.
"""

import os
import glob
import random
from datetime import datetime, timedelta
from pathlib import Path
import kagglehub
import numpy as np
import pandas as pd

# Set random seed for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Data Directory
DATA_DIR = Path(__file__).parent / "data"


def download_and_clean_employees() -> pd.DataFrame:
    """
    Downloads the IBM HR Attrition dataset from Kaggle and cleans it.
    Returns cleaned DataFrame for employees.csv.
    """
    print("[1/5] Downloading IBM HR dataset from Kaggle...")
    dataset_path = kagglehub.dataset_download("pavansubhasht/ibm-hr-analytics-attrition-dataset")
    print(f"    Downloaded to: {dataset_path}")

    # Find the CSV file in downloaded directory
    csv_files = glob.glob(os.path.join(dataset_path, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV file found in Kaggle download directory: {dataset_path}")

    raw_df = pd.read_csv(csv_files[0])
    print(f"    Raw dataset shape: {raw_df.shape}")

    # Rename EmployeeNumber -> employee_id
    raw_df = raw_df.rename(columns={"EmployeeNumber": "employee_id"})

    # Select requested columns
    keep_columns = [
        "employee_id",
        "Department",
        "JobRole",
        "Gender",
        "Age",
        "Education",
        "BusinessTravel",
        "YearsAtCompany",
        "JobLevel",
        "MonthlyIncome",
    ]

    employees_df = raw_df[keep_columns].copy()

    # Ensure employee_id is sorted
    employees_df = employees_df.sort_values(by="employee_id").reset_index(drop=True)
    print(f"    Cleaned employees dataset shape: {employees_df.shape}")
    return employees_df


def generate_onboarding_data(employees_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates synthetic onboarding data with 1 row per employee.
    Correlates tenure (YearsAtCompany) with onboarding status and dates,
    and correlates training completion percentage with onboarding duration.
    """
    print("[2/5] Generating synthetic onboarding dataset (onboarding.csv)...")
    onboarding_records = []
    base_date = datetime(2026, 7, 31)

    for _, row in employees_df.iterrows():
        emp_id = row["employee_id"]
        years = row["YearsAtCompany"]

        # Logical correlation: Recent hires (YearsAtCompany <= 1) are active/recent onboardings
        if years == 0:
            hire_offset_days = random.randint(10, 180)
            hire_date = base_date - timedelta(days=hire_offset_days)
            status_choice = random.choices(
                ["Completed", "In Progress", "Delayed"],
                weights=[0.60, 0.25, 0.15]
            )[0]
        elif years == 1:
            hire_offset_days = random.randint(180, 365)
            hire_date = base_date - timedelta(days=hire_offset_days)
            status_choice = random.choices(
                ["Completed", "In Progress", "Delayed"],
                weights=[0.85, 0.10, 0.05]
            )[0]
        else:
            hire_offset_days = min(int(years * 365) + random.randint(0, 60), 3650)
            hire_date = base_date - timedelta(days=hire_offset_days)
            status_choice = "Completed"

        orientation_completed = "Yes" if status_choice == "Completed" else random.choice(["Yes", "Yes", "No"])
        manager_assigned = "Yes" if status_choice != "Delayed" else random.choice(["Yes", "No"])
        buddy_assigned = "Yes" if status_choice == "Completed" else random.choice(["Yes", "No"])
        first_week_checkin = "Yes" if orientation_completed == "Yes" else random.choice(["Yes", "No"])

        if status_choice == "Completed":
            training_pct = round(random.uniform(80.0, 100.0), 1)
            onboarding_days = random.randint(5, 18)
            completion_date = (hire_date + timedelta(days=onboarding_days)).strftime("%Y-%m-%d")
        elif status_choice == "In Progress":
            training_pct = round(random.uniform(40.0, 79.9), 1)
            onboarding_days = random.randint(15, 30)
            completion_date = ""
        else:  # Delayed
            training_pct = round(random.uniform(15.0, 50.0), 1)
            onboarding_days = random.randint(25, 45)
            completion_date = ""

        onboarding_records.append({
            "employee_id": emp_id,
            "orientation_completed": orientation_completed,
            "training_completion_percent": training_pct,
            "onboarding_days": onboarding_days,
            "onboarding_status": status_choice,
            "manager_assigned": manager_assigned,
            "buddy_assigned": buddy_assigned,
            "first_week_checkin": first_week_checkin,
            "onboarding_completion_date": completion_date,
        })

    onboarding_df = pd.DataFrame(onboarding_records)
    print(f"    Generated onboarding dataset shape: {onboarding_df.shape}")
    return onboarding_df


def generate_support_tickets_data(
    employees_df: pd.DataFrame, onboarding_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Generates synthetic support ticket dataset (~800 to 1200 rows).
    Correlates training completion % and tenure with ticket volume and issue types.
    Higher priority tickets take longer to resolve.
    """
    print("[3/5] Generating synthetic support tickets dataset (support_tickets.csv)...")
    ticket_records = []
    ticket_id_counter = 10001
    base_date = datetime(2026, 7, 31)

    merged_emp = employees_df.merge(onboarding_df, on="employee_id")

    onboarding_issues = ["Laptop Setup", "Email Setup", "VPN Access", "MFA Issue", "Software Installation", "GitHub Access"]
    general_issues = ["Password Reset", "Network Connectivity", "VPN Access", "Software Installation", "MFA Issue"]

    teams = {
        "VPN Access": "SecOps",
        "MFA Issue": "SecOps",
        "Email Setup": "IT Helpdesk",
        "Laptop Setup": "IT Helpdesk",
        "Password Reset": "IT Helpdesk",
        "Software Installation": "IT Helpdesk",
        "GitHub Access": "DevOps",
        "Network Connectivity": "Infrastructure",
    }

    priorities = ["Low", "Medium", "High", "Critical"]
    priority_weights = [0.40, 0.35, 0.18, 0.07]

    res_hours_range = {
        "Low": (0.5, 4.0),
        "Medium": (3.0, 12.0),
        "High": (8.0, 36.0),
        "Critical": (24.0, 72.0),
    }

    for _, row in merged_emp.iterrows():
        emp_id = row["employee_id"]
        training_pct = row["training_completion_percent"]
        years = row["YearsAtCompany"]

        if training_pct < 60.0 or years <= 1:
            num_tickets = random.choices([0, 1, 2, 3, 4], weights=[0.20, 0.35, 0.25, 0.15, 0.05])[0]
        elif training_pct < 85.0:
            num_tickets = random.choices([0, 1, 2], weights=[0.45, 0.40, 0.15])[0]
        else:
            num_tickets = random.choices([0, 1, 2], weights=[0.65, 0.30, 0.05])[0]

        for _ in range(num_tickets):
            created_days_ago = random.randint(1, 60)
            created_date = base_date - timedelta(days=created_days_ago)

            if years <= 1:
                issue_type = random.choice(onboarding_issues)
            else:
                issue_type = random.choice(general_issues)

            priority = random.choices(priorities, weights=priority_weights)[0]
            assigned_team = teams[issue_type]

            low_h, high_h = res_hours_range[priority]
            resolution_hours = round(random.uniform(low_h, high_h), 1)

            if created_days_ago < 3 and priority in ["High", "Critical"]:
                status = random.choice(["In Progress", "Pending", "Resolved"])
            else:
                status = random.choices(["Resolved", "Closed"], weights=[0.70, 0.30])[0]

            res_val = resolution_hours if status in ["Resolved", "Closed"] else np.nan

            ticket_records.append({
                "ticket_id": f"TCK-{ticket_id_counter}",
                "employee_id": emp_id,
                "created_date": created_date.strftime("%Y-%m-%d"),
                "issue_type": issue_type,
                "priority": priority,
                "resolution_hours": res_val,
                "status": status,
                "assigned_team": assigned_team,
            })
            ticket_id_counter += 1

    tickets_df = pd.DataFrame(ticket_records)
    print(f"    Generated support tickets dataset shape: {tickets_df.shape}")
    return tickets_df


def generate_tool_usage_data(
    employees_df: pd.DataFrame, onboarding_df: pd.DataFrame, tickets_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Generates synthetic tool usage dataset (~3000 to 5000 rows).
    Incorporate department-specific tool affinity and employee productivity/friction logic.
    """
    print("[4/5] Generating synthetic tool usage dataset (tool_usage.csv)...")
    
    ticket_counts = tickets_df.groupby("employee_id").size().to_dict()
    merged_emp = employees_df.merge(onboarding_df, on="employee_id")

    dept_tools = {
        "Research & Development": {
            "tools": ["VS Code", "GitHub", "Jira", "Slack", "Confluence", "Notion"],
            "weights": [0.30, 0.25, 0.20, 0.15, 0.05, 0.05],
            "devices": ["MacBook Pro", "Linux Workstation", "Windows Laptop"],
            "device_weights": [0.50, 0.35, 0.15],
        },
        "Sales": {
            "tools": ["Google Workspace", "Notion", "Slack", "Confluence", "Jira"],
            "weights": [0.40, 0.25, 0.20, 0.10, 0.05],
            "devices": ["MacBook Pro", "Windows Laptop", "Mobile (iOS)", "Mobile (Android)"],
            "device_weights": [0.40, 0.40, 0.10, 0.10],
        },
        "Human Resources": {
            "tools": ["Notion", "Google Workspace", "Slack", "Confluence"],
            "weights": [0.35, 0.35, 0.20, 0.10],
            "devices": ["Windows Laptop", "MacBook Pro"],
            "device_weights": [0.60, 0.40],
        },
    }

    tool_features = {
        "VS Code": ["Code Commit", "Debugging", "Extension Usage", "Workspace Config"],
        "GitHub": ["Pull Request Review", "Code Commit", "Issue Tracking", "Repo Clone"],
        "Jira": ["Sprint Board View", "Ticket Creation", "Backlog Grooming", "Status Update"],
        "Slack": ["Channel Message", "Direct Message", "Huddle Call", "Thread Reply"],
        "Confluence": ["Document Edit", "Page Creation", "Wiki Search", "Comment"],
        "Google Workspace": ["Doc Collaboration", "Sheet Editing", "Slide Presentation", "Drive Share"],
        "Notion": ["Wiki Editing", "Task Tracking", "Database Update", "Template Creation"],
    }

    usage_records = []
    usage_id_counter = 1
    base_date = datetime(2026, 7, 31)

    date_range = [(base_date - timedelta(days=d)).strftime("%Y-%m-%d") for d in range(1, 31)]

    for _, row in merged_emp.iterrows():
        emp_id = row["employee_id"]
        dept = row["Department"]
        training_pct = row["training_completion_percent"]
        onboarding_days = row["onboarding_days"]
        num_tickets = ticket_counts.get(emp_id, 0)

        config = dept_tools.get(dept, dept_tools["Research & Development"])

        if training_pct >= 80.0 and num_tickets <= 1 and onboarding_days <= 14:
            num_days_active = random.randint(3, 5)
        elif num_tickets >= 3 or training_pct < 50.0:
            num_days_active = random.randint(1, 2)
        else:
            num_days_active = random.randint(2, 4)

        active_dates = random.sample(date_range, num_days_active)

        for log_date in active_dates:
            num_logs = random.randint(1, 2)
            chosen_tools = random.choices(config["tools"], weights=config["weights"], k=num_logs)

            for tool in chosen_tools:
                device = random.choices(config["devices"], weights=config["device_weights"])[0]
                feature = random.choice(tool_features[tool])

                if num_tickets >= 3 or training_pct < 50.0:
                    active_mins = random.randint(10, 90)
                    logins = random.randint(1, 4)
                else:
                    active_mins = random.randint(45, 360)
                    logins = random.randint(3, 18)

                usage_records.append({
                    "usage_id": f"USG-{usage_id_counter:06d}",
                    "employee_id": emp_id,
                    "date": log_date,
                    "tool_name": tool,
                    "login_count": logins,
                    "active_minutes": active_mins,
                    "feature_used": feature,
                    "device_type": device,
                })
                usage_id_counter += 1

    usage_df = pd.DataFrame(usage_records)
    print(f"    Generated tool usage dataset shape: {usage_df.shape}")
    return usage_df


def validate_datasets(
    emp_df: pd.DataFrame,
    onb_df: pd.DataFrame,
    tool_df: pd.DataFrame,
    tck_df: pd.DataFrame,
):
    """
    Performs assertions and validation checks on datasets.
    """
    print("\n[5/5] Running validation checks across all datasets...")

    emp_ids = set(emp_df["employee_id"])

    # Check 1: Referential integrity
    onb_ids = set(onb_df["employee_id"])
    tool_ids = set(tool_df["employee_id"])
    tck_ids = set(tck_df["employee_id"])

    assert onb_ids.issubset(emp_ids), "Validation Error: employee_id in onboarding.csv does not exist in employees.csv!"
    assert tool_ids.issubset(emp_ids), "Validation Error: employee_id in tool_usage.csv does not exist in employees.csv!"
    assert tck_ids.issubset(emp_ids), "Validation Error: employee_id in support_tickets.csv does not exist in employees.csv!"
    print("    [PASS] Referential integrity checks passed: All foreign keys exist in employees.csv.")

    # Check 2: onboarding.csv row count & key uniqueness
    assert len(onb_df) == len(emp_df), f"Validation Error: onboarding.csv has {len(onb_df)} rows, expected {len(emp_df)}."
    assert onb_df["employee_id"].is_unique, "Validation Error: Duplicate employee_ids found in onboarding.csv!"
    assert len(emp_ids - onb_ids) == 0, "Validation Error: Missing employee_ids in onboarding.csv!"
    print("    [PASS] Onboarding key uniqueness and 1:1 ratio checks passed.")

    # Check 3: Print shapes
    print("\n" + "=" * 60)
    print("DATASET SHAPES:")
    print(f"  employees.csv:       {emp_df.shape}")
    print(f"  onboarding.csv:      {onb_df.shape}")
    print(f"  tool_usage.csv:      {tool_df.shape}")
    print(f"  support_tickets.csv: {tck_df.shape}")
    print("=" * 60)

    # Check 4: Print basic stats
    print("\n--- Summary Statistics ---")
    print("\nEmployees (MonthlyIncome & Age):")
    print(emp_df[["Age", "MonthlyIncome", "YearsAtCompany"]].describe().round(2))

    print("\nOnboarding (training_completion_percent & onboarding_days):")
    print(onb_df[["training_completion_percent", "onboarding_days"]].describe().round(2))

    print("\nTool Usage (login_count & active_minutes):")
    print(tool_df[["login_count", "active_minutes"]].describe().round(2))

    print("\nSupport Tickets (resolution_hours):")
    print(tck_df[["resolution_hours"]].describe().round(2))

    # Check 5: Print samples
    print("\n--- Sample Data Head ---")
    print("\nemployees.csv sample:")
    print(emp_df.head(3).to_string())

    print("\nonboarding.csv sample:")
    print(onb_df.head(3).to_string())

    print("\ntool_usage.csv sample:")
    print(tool_df.head(3).to_string())

    print("\nsupport_tickets.csv sample:")
    print(tck_df.head(3).to_string())
    print("\nValidation completed successfully!\n")


def main():
    """Main execution function."""
    print("=" * 60)
    print("STARTING DATASET PREPARATION & GENERATION PIPELINE")
    print("=" * 60)

    # Step 1: Clean Employees Dataset
    emp_df = download_and_clean_employees()

    # Step 2: Generate Onboarding Dataset
    onb_df = generate_onboarding_data(emp_df)

    # Step 3: Generate Support Tickets Dataset
    tck_df = generate_support_tickets_data(emp_df, onb_df)

    # Step 4: Generate Tool Usage Dataset
    tool_df = generate_tool_usage_data(emp_df, onb_df, tck_df)

    # Step 5: Validate
    validate_datasets(emp_df, onb_df, tool_df, tck_df)

    # Step 6: Save CSVs
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    emp_df.to_csv(DATA_DIR / "employees.csv", index=False)
    onb_df.to_csv(DATA_DIR / "onboarding.csv", index=False)
    tool_df.to_csv(DATA_DIR / "tool_usage.csv", index=False)
    tck_df.to_csv(DATA_DIR / "support_tickets.csv", index=False)

    print(f"[SUCCESS] Saved all CSV datasets to directory: {DATA_DIR.resolve()}")


if __name__ == "__main__":
    main()
