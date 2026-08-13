import pandas as pd
import pickle
import shap
import matplotlib.pyplot as plt

def run_model_interpretation():
    print("Starting Model Interpretation...")
    
    # Load model and test data
    with open('best_model.pkl', 'rb') as f:
        model = pickle.load(f)
        
    X_test = pd.read_csv('X_test.csv')
    
    # Create SHAP Explainer
    # TreeExplainer is optimized for tree-based models (RF, XGBoost)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    
    # For some models/versions, shap_values is a list (one per class). We want the positive class (friction = 1)
    if isinstance(shap_values, list):
        shap_values_pos = shap_values[1]
    else:
        shap_values_pos = shap_values
    
    print("Generating SHAP summary plot...")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values_pos, X_test, show=False)
    plt.tight_layout()
    plt.savefig('shap_summary.png', dpi=300)
    plt.close()
    print("Saved 'shap_summary.png'.")
    
    # Print out top features by mean absolute SHAP value
    mean_abs_shap = abs(shap_values_pos).mean(axis=0)
    feature_importance = pd.DataFrame({
        'Feature': X_test.columns,
        'Mean_Abs_SHAP': mean_abs_shap
    }).sort_values(by='Mean_Abs_SHAP', ascending=False)
    
    print("\n--- Top Bottlenecks (Feature Importance) ---")
    print(feature_importance.head(5))
    
if __name__ == '__main__':
    run_model_interpretation()
