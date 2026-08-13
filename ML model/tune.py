import nbformat

with open('04_model_training_evaluation.ipynb', 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

new_code = """def run_model_training():
    print("Starting Model Training & Evaluation...")
    import pandas as pd
    from sklearn.model_selection import train_test_split, GridSearchCV
    from sklearn.ensemble import RandomForestClassifier
    from xgboost import XGBClassifier
    from sklearn.metrics import classification_report, roc_auc_score
    import pickle
    
    df = pd.read_csv('engineered_data.csv')
    
    # Separate features and target
    X = df.drop(columns=['employee_id', 'high_friction'])
    y = df['high_friction']
    
    # Train-test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Training set size: {X_train.shape[0]}")
    print(f"Test set size: {X_test.shape[0]}\\n")
    
    # Model 1: Random Forest
    print("--- Training Random Forest (Tuned) ---")
    rf_params = {
        'n_estimators': [100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
    rf_grid = GridSearchCV(RandomForestClassifier(random_state=42), rf_params, cv=3, scoring='accuracy', n_jobs=-1)
    rf_grid.fit(X_train, y_train)
    rf_model = rf_grid.best_estimator_
    print("Best RF Params:", rf_grid.best_params_)
    rf_preds = rf_model.predict(X_test)
    rf_probs = rf_model.predict_proba(X_test)[:, 1]
    
    print(classification_report(y_test, rf_preds))
    print(f"RF ROC-AUC: {roc_auc_score(y_test, rf_probs):.4f}\\n")
    
    # Model 2: XGBoost
    print("--- Training XGBoost (Tuned) ---")
    xgb_params = {
        'n_estimators': [100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.8, 1.0]
    }
    xgb_grid = GridSearchCV(XGBClassifier(random_state=42, eval_metric='logloss'), xgb_params, cv=3, scoring='accuracy', n_jobs=-1)
    xgb_grid.fit(X_train, y_train)
    xgb_model = xgb_grid.best_estimator_
    print("Best XGB Params:", xgb_grid.best_params_)
    
    xgb_preds = xgb_model.predict(X_test)
    xgb_probs = xgb_model.predict_proba(X_test)[:, 1]
    
    print(classification_report(y_test, xgb_preds))
    print(f"XGB ROC-AUC: {roc_auc_score(y_test, xgb_probs):.4f}\\n")
    
    # Select best model
    if roc_auc_score(y_test, rf_probs) > roc_auc_score(y_test, xgb_probs):
        best_model = rf_model
        print("Selecting Random Forest as the final model.")
    else:
        best_model = xgb_model
        print("Selecting XGBoost as the final model.")
    
    # Save the model
    with open('best_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    print("Saved 'best_model.pkl'.")
    
    # Save test data for SHAP interpretation later
    X_test.to_csv('X_test.csv', index=False)
"""

nb.cells[1].source = new_code

with open('04_model_training_evaluation.ipynb', 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)
