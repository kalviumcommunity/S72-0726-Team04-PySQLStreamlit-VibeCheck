import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

def run_feature_engineering():
    print("Starting Label & Feature Engineering...")
    df = pd.read_csv('master_data.csv')
    
    # 1. Create the composite target label 'high_friction'
    # Condition 1: Onboarding takes > 15 days (approx 75th percentile)
    cond1 = df['onboarding_days'] > 15
    # Condition 2: Training completion < 85%
    cond2 = df['training_completion_percent'] < 85
    # Condition 3: 2+ tickets OR 1+ High priority ticket
    cond3 = (df['total_tickets'] >= 2) | (df['high_priority_tickets'] >= 1)
    # Condition 4: Status is stuck
    cond4 = df['onboarding_status'].isin(['In Progress', 'Delayed'])
    
    df['high_friction'] = (cond1 | cond2 | cond3 | cond4).astype(int)
    
    print("Label 'high_friction' Distribution:")
    print(df['high_friction'].value_counts(normalize=True))
    
    # 2. Select predictive features (Early Signals)
    # Drop columns that would cause data leakage (future knowledge or direct components of the label)
    columns_to_drop = [
        'onboarding_days', 
        'training_completion_percent', 
        'total_tickets', 
        'high_priority_tickets',
        'avg_resolution_hours',
        'onboarding_status',
        'onboarding_completion_date'
    ]
    
    # We keep: Department, JobRole, Gender, Age, Education, BusinessTravel, YearsAtCompany, 
    # JobLevel, MonthlyIncome, orientation_completed, manager_assigned, buddy_assigned, 
    # first_week_checkin, total_tool_actions, unique_tools_used
    
    features_df = df.drop(columns=columns_to_drop)
    
    # 3. Handle Categorical Encoding
    categorical_cols = ['Department', 'JobRole', 'Gender', 'BusinessTravel', 'orientation_completed', 'manager_assigned', 'buddy_assigned', 'first_week_checkin']
    
    # Apply Label Encoding for simplicity in this baseline (One-Hot is also good, but Label is fine for tree models)
    le = LabelEncoder()
    for col in categorical_cols:
        if col in features_df.columns:
            features_df[col] = features_df[col].astype(str)
            features_df[col] = le.fit_transform(features_df[col])
            
    print(f"\nFinal Features Dataset Shape: {features_df.shape}")
    
    # Save the engineered dataset
    features_df.to_csv('engineered_data.csv', index=False)
    print("\nSaved 'engineered_data.csv'.")

if __name__ == '__main__':
    run_feature_engineering()
