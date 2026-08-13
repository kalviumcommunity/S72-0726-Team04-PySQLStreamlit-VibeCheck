import pandas as pd
import numpy as np

def run_cleaning_and_merge():
    print("Starting Data Cleaning and Merging...")
    
    # 1. Load data
    employees = pd.read_csv('../data/employees.csv')
    onboarding = pd.read_csv('../data/onboarding.csv')
    support_tickets = pd.read_csv('../data/support_tickets.csv')
    tool_usage = pd.read_csv('../data/tool_usage.csv')
    
    # 2. Clean Data
    # For onboarding missing completion dates, they correspond to 'In Progress' or 'Delayed' usually.
    # We will leave NaT for now, as we might use the status instead.
    
    # Support tickets missing resolution hours: fill with median
    median_res_hours = support_tickets['resolution_hours'].median()
    support_tickets['resolution_hours'] = support_tickets['resolution_hours'].fillna(median_res_hours)
    
    # 3. Aggregate Support Tickets per Employee
    # Convert dates to datetime if they exist, but let's just do basic aggregation first.
    ticket_agg = support_tickets.groupby('employee_id').agg(
        total_tickets=('ticket_id', 'count'),
        high_priority_tickets=('priority', lambda x: (x.isin(['High', 'Critical'])).sum()),
        avg_resolution_hours=('resolution_hours', 'mean')
    ).reset_index()
    
    # 4. Aggregate Tool Usage per Employee
    tool_agg = tool_usage.groupby('employee_id').agg(
        total_tool_actions=('usage_id', 'count'),
        unique_tools_used=('feature_used', 'nunique')
    ).reset_index()
    
    # 5. Merge everything together
    # Base is employees
    master_df = employees.merge(onboarding, on='employee_id', how='left')
    master_df = master_df.merge(ticket_agg, on='employee_id', how='left')
    master_df = master_df.merge(tool_agg, on='employee_id', how='left')
    
    # Fill missing values for employees who didn't open tickets or use tools
    master_df['total_tickets'] = master_df['total_tickets'].fillna(0)
    master_df['high_priority_tickets'] = master_df['high_priority_tickets'].fillna(0)
    master_df['total_tool_actions'] = master_df['total_tool_actions'].fillna(0)
    master_df['unique_tools_used'] = master_df['unique_tools_used'].fillna(0)
    
    print(f"Master Dataset Shape: {master_df.shape}")
    print("Master Dataset Columns:")
    print(master_df.columns.tolist())
    print("\nMissing values in master:")
    print(master_df.isnull().sum()[master_df.isnull().sum() > 0])
    
    # Save the master dataset for the next step
    master_df.to_csv('master_data.csv', index=False)
    print("\nSaved 'master_data.csv'.")

if __name__ == '__main__':
    run_cleaning_and_merge()
