import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda():
    print("Starting EDA...")
    
    # Load datasets
    employees = pd.read_csv('../data/employees.csv')
    onboarding = pd.read_csv('../data/onboarding.csv')
    support_tickets = pd.read_csv('../data/support_tickets.csv')
    tool_usage = pd.read_csv('../data/tool_usage.csv')
    
    def summarize_df(df, name):
        print(f"--- {name} ---")
        print(f"Shape: {df.shape}")
        print("Missing values:")
        missing = df.isnull().sum()
        print(missing[missing > 0] if missing.sum() > 0 else "No missing values")
        print("-" * 30)
    
    summarize_df(employees, 'Employees')
    summarize_df(onboarding, 'Onboarding')
    summarize_df(support_tickets, 'Support Tickets')
    summarize_df(tool_usage, 'Tool Usage')
    
    print("\n--- Value Counts for Key Columns ---")
    
    print("\nEmployees - Department:")
    print(employees['Department'].value_counts())
    
    if 'onboarding_status' in onboarding.columns:
        print("\nOnboarding - Status:")
        print(onboarding['onboarding_status'].value_counts())
        
    print("\nSupport Tickets - Priority:")
    if 'priority' in support_tickets.columns:
        print(support_tickets['priority'].value_counts())
    else:
        print("priority not found, let's look at available columns:", support_tickets.columns.tolist())
        
    print("\nSupport Tickets - Status:")
    if 'status' in support_tickets.columns:
        print(support_tickets['status'].value_counts())

    print("\nEDA Completed.")

if __name__ == '__main__':
    run_eda()
