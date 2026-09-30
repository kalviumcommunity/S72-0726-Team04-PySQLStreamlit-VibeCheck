from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import fetch_table_as_df
import pandas as pd
import os
import pickle

ML_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ML model")
MODEL_PATH = os.path.join(ML_DIR, "best_model.pkl")
DATA_PATH = os.path.join(ML_DIR, "engineered_data.csv")
RISK_SCORES_PATH = os.path.join(ML_DIR, "risk_scores.csv")

def get_ml_predictions() -> pd.DataFrame:
    """Safely fetch ML predictions using trained model, falling back to precomputed risk_scores.csv if needed."""
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(DATA_PATH):
            with open(MODEL_PATH, "rb") as f:
                ml_model = pickle.load(f)
            ml_data = pd.read_csv(DATA_PATH)
            X = ml_data.drop(columns=['employee_id', 'high_friction'], errors='ignore')
            ml_data['predicted_risk'] = ml_model.predict_proba(X)[:, 1] * 100
            return ml_data[['employee_id', 'predicted_risk']]
    except Exception as e:
        print(f"Notice: Standard ML model predict_proba skipped ({e}), utilizing risk scores dataset.")

    if os.path.exists(RISK_SCORES_PATH):
        try:
            rs_data = pd.read_csv(RISK_SCORES_PATH)
            return rs_data[['employee_id', 'risk_score']].rename(columns={'risk_score': 'predicted_risk'})
        except Exception as e:
            print(f"Error reading risk_scores.csv: {e}")

    return pd.DataFrame(columns=['employee_id', 'predicted_risk'])

class DashboardKPIsView(APIView):
    def get(self, request):
        df_onb = fetch_table_as_df("onboarding")
        df_tickets = fetch_table_as_df("support_tickets")
        
        onb_days_clean = pd.to_numeric(df_onb['onboarding_days'], errors='coerce').dropna()
        avg_onboarding_days = float(onb_days_clean.mean()) if not onb_days_clean.empty else 0.0
        
        time_to_value = float(avg_onboarding_days + 7.0)
        
        new_hire_ids = df_onb['employee_id'].dropna().unique()
        new_hire_tickets = df_tickets[df_tickets['employee_id'].isin(new_hire_ids)]
        avg_tickets = float(len(new_hire_tickets) / len(new_hire_ids)) if len(new_hire_ids) > 0 else 0.0
        
        return Response({
            "avg_onboarding_days": float(round(avg_onboarding_days, 1)),
            "time_to_value": float(round(time_to_value, 1)),
            "avg_tickets": float(round(avg_tickets, 1))
        })

class FrictionChartsView(APIView):
    def get(self, request):
        df_onb = fetch_table_as_df("onboarding")
        df_tickets = fetch_table_as_df("support_tickets")
        df_tools = fetch_table_as_df("tool_usage")
        
        # 1. Scatter plot data
        ticket_counts = df_tickets.groupby('employee_id').size().reset_index(name='ticket_count')
        scatter_merged = pd.merge(df_onb[['employee_id', 'training_completion_percent']], ticket_counts, on='employee_id', how='left').fillna(0)
        
        # 2. Top Bottlenecks by issue_type
        blockers = df_tickets['issue_type'].value_counts().reset_index()
        blockers.columns = ['issue_type', 'count']
        
        # 3. Tool Adoption Curve
        grouped_tools = df_tools.groupby(['date', 'tool_name'])['active_minutes'].mean().reset_index()
        tool_adoption = grouped_tools.pivot(index='date', columns='tool_name', values='active_minutes').fillna(0).reset_index()
        
        # 4. Buddy Impact (Training % by buddy_assigned)
        buddy_impact = df_onb.groupby('buddy_assigned')['training_completion_percent'].mean().reset_index()

        return Response({
            "scatter": scatter_merged.to_dict('records'),
            "blockers": blockers.to_dict('records'),
            "tool_adoption": tool_adoption.to_dict('records'),
            "buddy_impact": buddy_impact.to_dict('records')
        })

class EmployeeFrictionTableView(APIView):
    def get(self, request):
        df_emp = fetch_table_as_df("employees")
        df_onb = fetch_table_as_df("onboarding")
        df_tickets = fetch_table_as_df("support_tickets")
        
        ticket_stats = df_tickets.groupby('employee_id').agg(
            ticket_count=('ticket_id', 'count'),
            avg_resolution=('resolution_hours', 'mean')
        ).reset_index()
        
        merged = pd.merge(df_emp[['employee_id', 'JobRole', 'Department']], df_onb[['employee_id', 'onboarding_status', 'training_completion_percent']], on='employee_id')
        merged = pd.merge(merged, ticket_stats, on='employee_id', how='left').fillna(0)
        manager = request.GET.get('manager_assigned')
        if manager:
            if 'manager_assigned' in merged.columns:
                merged = merged[merged['manager_assigned'].str.lower() == manager.lower()]
        ml_preds = get_ml_predictions()
        merged = pd.merge(merged, ml_preds, on='employee_id', how='left').fillna({'predicted_risk': 0})
        
        # Calculate friction_score: (Ticket Count * 10) + (Avg Resolution Hours * 2) - (Training % * 0.5)
        merged['friction_score'] = (merged['ticket_count'] * 10) + (merged['avg_resolution'] * 2) - (merged['training_completion_percent'] * 0.5)
        
        # Clamp between 0 and 100
        merged['friction_score'] = merged['friction_score'].clip(lower=0, upper=100)
        
        merged = merged.sort_values(by='friction_score', ascending=False)
        return Response(merged.head(100).to_dict('records'))

class EmployeeDetailView(APIView):
    def get(self, request, employee_id):
        df_emp = fetch_table_as_df("employees")
        df_onb = fetch_table_as_df("onboarding")
        df_tickets = fetch_table_as_df("support_tickets")
        df_tools = fetch_table_as_df("tool_usage")
        ml_preds = get_ml_predictions()

        if df_emp.empty or df_onb.empty:
            return Response({"error": "Core datasets missing"}, status=503)

        emp_row = df_emp[df_emp['employee_id'] == employee_id]
        if emp_row.empty:
            return Response({"error": "Employee not found"}, status=404)

        emp_info = emp_row.iloc[0].to_dict()
        
        onb_row = df_onb[df_onb['employee_id'] == employee_id]
        onb_info = onb_row.iloc[0].to_dict() if not onb_row.empty else {}

        emp_tickets = df_tickets[df_tickets['employee_id'] == employee_id]
        tickets_list = emp_tickets.to_dict('records')

        emp_tools = df_tools[df_tools['employee_id'] == employee_id]
        tools_list = emp_tools.to_dict('records')

        ticket_count = len(emp_tickets)
        avg_res = float(emp_tickets['resolution_hours'].mean()) if ticket_count > 0 and 'resolution_hours' in emp_tickets else 0.0
        training_pct = float(onb_info.get('training_completion_percent', 0.0))

        friction_score = (ticket_count * 10) + (avg_res * 2) - (training_pct * 0.5)
        friction_score = max(0.0, min(100.0, friction_score))

        pred_risk_row = ml_preds[ml_preds['employee_id'] == employee_id]
        predicted_risk = float(pred_risk_row.iloc[0]['predicted_risk']) if not pred_risk_row.empty else 0.0

        detail = {
            "employee_id": int(employee_id),
            "JobRole": str(emp_info.get("JobRole", "N/A")),
            "Department": str(emp_info.get("Department", "N/A")),
            "Gender": str(emp_info.get("Gender", "N/A")),
            "Age": int(emp_info.get("Age")) if pd.notnull(emp_info.get("Age")) else None,
            "YearsAtCompany": int(emp_info.get("YearsAtCompany")) if pd.notnull(emp_info.get("YearsAtCompany")) else None,
            "onboarding_status": str(onb_info.get("onboarding_status", "Unknown")),
            "training_completion_percent": float(round(training_pct, 1)),
            "onboarding_days": int(onb_info.get("onboarding_days", 0)) if pd.notnull(onb_info.get("onboarding_days")) else 0,
            "manager_assigned": str(onb_info.get("manager_assigned", "N/A")),
            "buddy_assigned": str(onb_info.get("buddy_assigned", "N/A")),
            "friction_score": float(round(friction_score, 1)),
            "predicted_risk": float(round(predicted_risk, 1)),
            "metrics": {"total_tickets": ticket_count, "avg_resolution_hrs": float(round(avg_res, 1))},
            "tickets": tickets_list,
            "tool_usage": tools_list
        }
        return Response(detail)

class DepartmentKPIsView(APIView):
    def get(self, request):
        df_emp = fetch_table_as_df("employees")
        df_onb = fetch_table_as_df("onboarding")
        if df_emp.empty or df_onb.empty: return Response([])
        merged = pd.merge(df_emp, df_onb, on='employee_id')
        dept_kpis = merged.groupby('Department')['training_completion_percent'].mean().reset_index()
        dept_kpis.columns = ['department', 'avg_training_percent']
        return Response(dept_kpis.to_dict('records'))
