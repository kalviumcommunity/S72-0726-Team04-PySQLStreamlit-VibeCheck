import pandas as pd
import pickle

def run_scoring_pipeline():
    print("Starting Scoring Pipeline...")
    
    # 1. Load the engineered data
    # In production, this would be fresh data coming from the live databases.
    # For this exercise, we score all historical employees.
    df = pd.read_csv('engineered_data.csv')
    
    # Extract employee_id and the features used by the model
    employee_ids = df['employee_id']
    X_score = df.drop(columns=['employee_id', 'high_friction'])
    
    # 2. Load the trained final model
    with open('best_model.pkl', 'rb') as f:
        model = pickle.load(f)
        
    # 3. Generate Predictions and Probabilities
    # We want the probability of class 1 (high_friction)
    probs = model.predict_proba(X_score)[:, 1]
    
    # Convert to a 0-100 risk score
    risk_scores = (probs * 100).round(1)
    
    # 4. Create the final output table
    risk_table = pd.DataFrame({
        'employee_id': employee_ids,
        'risk_score': risk_scores,
        'risk_level': ['High' if score >= 70 else 'Medium' if score >= 40 else 'Low' for score in risk_scores]
    })
    
    # Merge some basic info for the dashboard (like Department) from master_data
    master = pd.read_csv('master_data.csv')
    dashboard_table = risk_table.merge(master[['employee_id', 'Department', 'JobRole']], on='employee_id', how='left')
    
    print("\nRisk Table Sample:")
    print(dashboard_table.head())
    
    print("\nRisk Level Distribution:")
    print(dashboard_table['risk_level'].value_counts())
    
    # 5. Export for Dashboard consumption
    dashboard_table.to_csv('risk_scores.csv', index=False)
    print("\nSaved 'risk_scores.csv'. Pipeline complete.")

if __name__ == '__main__':
    run_scoring_pipeline()
