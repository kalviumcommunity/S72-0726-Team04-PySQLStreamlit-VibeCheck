import os
import subprocess
import time

branches_data = [
    ('vedant/feat-caching-kpis', 'feat: Add Caching for KPI Dashboard', 'Improves the load time of the dashboard by caching the KPI results for 15 minutes. Prevents redundant pandas calculations.'),
    ('vedant/feat-pagination', 'feat: Implement Pagination for Employee Table', 'Improves performance by paginating the EmployeeFrictionTableView, returning 20 records per page.'),
    ('vedant/feat-department-filter', 'feat: Add Department Filtering', 'Allows frontend to pass a department query parameter to filter the employee list.'),
    ('vedant/feat-export-csv', 'feat: CSV Export Endpoint for Employees', 'Creates a new endpoint returning a downloadable CSV of the friction table for HR reporting.'),
    ('vedant/fix-error-handling', 'fix: Improve Data Fetching Error Handling', 'Wraps data fetching in try-except blocks to prevent 500 errors when datasets are missing.'),
    ('vedant/feat-health-check', 'feat: Add Health Check Endpoint', 'Adds a simple /api/health/ endpoint for uptime monitoring and load balancers.'),
    ('vedant/feat-swagger-docs', 'feat: Setup Swagger API Documentation', 'Integrates drf-yasg to auto-generate Swagger UI documentation for all endpoints.'),
    ('vedant/feat-cors-config', 'chore: Configure CORS Headers', 'Adds django-cors-headers to settings to allow Next.js frontend to securely request data.'),
    ('vedant/feat-search-employee', 'feat: Add Employee Search Functionality', 'Adds query param support for searching employees by name or ID in the table view.'),
    ('vedant/feat-dynamic-sorting', 'feat: Dynamic Sorting for Friction Table', 'Allows the employee table to be sorted dynamically based on user-selected columns.'),
    ('vedant/feat-configurable-weights', 'feat: Configurable Friction Score Weights', 'Moves the hardcoded multipliers for friction score into the settings for easier tuning.'),
    ('vedant/feat-date-range-filter', 'feat: Date Range Filtering for KPIs', 'Adds start_date and end_date parameters to filter dashboard KPIs chronologically.'),
    ('vedant/feat-tool-usage-agg', 'feat: Tool Usage Aggregation Endpoint', 'Creates an endpoint specifically for aggregating active minutes per tool.'),
    ('vedant/feat-buddy-stats', 'feat: Buddy Impact Analysis Endpoint', 'Exposes buddy program impact stats directly through a dedicated view.'),
    ('vedant/feat-ml-fallback-logs', 'feat: ML Model Fallback Logging', 'Adds standard Python logging when the primary ML model fails and falls back to CSV.'),
    ('vedant/feat-high-risk-flags', 'feat: Flag High-Risk Employees', 'Injects a high_risk_flag boolean into the employee detail response if score > 90.'),
    ('vedant/feat-api-throttling', 'feat: Implement API Rate Limiting', 'Adds AnonRateThrottle and UserRateThrottle to DRF settings to prevent API abuse.'),
    ('vedant/feat-custom-exceptions', 'feat: Custom Exception Handlers', 'Implements a custom exception handler that returns standardized JSON errors.'),
    ('vedant/feat-refresh-data', 'feat: Cache Invalidation Endpoint', 'Adds a POST endpoint to clear server cache and force reload of Pandas dataframes.'),
    ('vedant/test-kpi-view', 'test: Unit Tests for Dashboard KPIs', 'Adds Django TestCase for the DashboardKPIsView verifying accurate calculations.'),
    ('vedant/test-friction-table', 'test: Unit Tests for Friction Table', 'Adds Django TestCase for the EmployeeFrictionTableView checking pagination and score.'),
    ('vedant/feat-department-kpis', 'feat: Department-wise KPI Aggregation', 'Creates a new View that returns the KPI metrics grouped by Department.'),
    ('vedant/feat-ticket-resolution-metrics', 'feat: Detailed Ticket Resolution Metrics', 'Enhances the employee detail view with median and max resolution times.'),
    ('vedant/feat-onboarding-status-filter', 'feat: Onboarding Status Filtering', 'Adds a filter to the employee table to show only In Progress or Completed employees.'),
    ('vedant/feat-manager-view', 'feat: Manager-specific Data Filtering', 'Filters the employee list to only show reports for a given manager_id.')
]

def check_gh_cli():
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

if __name__ == '__main__':
    print("Checking for GitHub CLI (gh)...")
    if not check_gh_cli():
        print("Error: GitHub CLI is not installed or not available in PATH.")
        print("Please install it from https://cli.github.com/ and authenticate using 'gh auth login'")
        exit(1)
        
    print("Pushing branches and creating Pull Requests...")
    
    for i, (branch, title, body) in enumerate(branches_data, 1):
        print(f"\n--- [{i}/25] Processing {branch} ---")
        
        # Push the branch to remote
        print(f"Pushing branch {branch} to origin...")
        push_result = subprocess.run(['git', 'push', '-u', 'origin', branch], capture_output=True, text=True)
        if push_result.returncode != 0:
            print(f"Failed to push {branch}. Ensure you have write access to the repository.")
            print(push_result.stderr)
            continue
            
        # Create the PR
        print(f"Opening PR for {branch}...")
        pr_result = subprocess.run([
            'gh', 'pr', 'create',
            '--head', branch,
            '--base', 'main',
            '--title', title,
            '--body', body
        ], capture_output=True, text=True)
        
        if pr_result.returncode == 0:
            print(f"Successfully created PR! {pr_result.stdout.strip()}")
        else:
            print(f"Failed to create PR for {branch}.")
            print(pr_result.stderr)
            
        # Small delay to prevent hitting API rate limits too quickly
        time.sleep(2)
        
    print("\nFinished creating Pull Requests!")
