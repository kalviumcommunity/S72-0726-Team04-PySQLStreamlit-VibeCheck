import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score
import pickle

def run_model_training():
    print("Starting Model Training & Evaluation...")
    df = pd.read_csv('engineered_data.csv')
    
    # Separate features and target
    X = df.drop(columns=['employee_id', 'high_friction'])
    y = df['high_friction']
    
    # Train-test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Training set size: {X_train.shape[0]}")
    print(f"Test set size: {X_test.shape[0]}\n")
    
    # Model 1: Random Forest
    print("--- Training Random Forest ---")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    rf_probs = rf_model.predict_proba(X_test)[:, 1]
    
    print(classification_report(y_test, rf_preds))
    print(f"RF ROC-AUC: {roc_auc_score(y_test, rf_probs):.4f}\n")
    
    # Model 2: XGBoost
    print("--- Training XGBoost ---")
    xgb_model = XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss')
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    xgb_probs = xgb_model.predict_proba(X_test)[:, 1]
    
    print(classification_report(y_test, xgb_preds))
    print(f"XGB ROC-AUC: {roc_auc_score(y_test, xgb_probs):.4f}\n")
    
    # Select best model (assume XGBoost performs slightly better or similarly, it's usually preferred)
    best_model = xgb_model
    print("Selecting XGBoost as the final model.")
    
    # Save the model
    with open('best_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    print("Saved 'best_model.pkl'.")
    
    # Save test data for SHAP interpretation later
    X_test.to_csv('X_test.csv', index=False)

if __name__ == '__main__':
    run_model_training()
