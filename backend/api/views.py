from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import fetch_table_as_df
import pandas as pd

class DashboardKPIsView(APIView):
    def get(self, request):
        df_onb = fetch_table_as_df("onboarding")
        df_tickets = fetch_table_as_df("support_tickets")
        
        avg_onboarding_days = df_onb['onboarding_days'].mean()
        
        # Assume Time-to-Value is onboarding days + 7 as a metric
        time_to_value = avg_onboarding_days + 7
        
        new_hire_ids = df_onb['employee_id'].unique()
        new_hire_tickets = df_tickets[df_tickets['employee_id'].isin(new_hire_ids)]
        avg_tickets = len(new_hire_tickets) / len(new_hire_ids) if len(new_hire_ids) > 0 else 0
        
        return Response({
            "avg_onboarding_days": round(avg_onboarding_days, 1),
            "time_to_value": round(time_to_value, 1),
            "avg_tickets": round(avg_tickets, 1)
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
        
        # Calculate friction_score: (Ticket Count * 10) + (Avg Resolution Hours * 2) - (Training % * 0.5)
        merged['friction_score'] = (merged['ticket_count'] * 10) + (merged['avg_resolution'] * 2) - (merged['training_completion_percent'] * 0.5)
        
        # Clamp between 0 and 100
        merged['friction_score'] = merged['friction_score'].clip(lower=0, upper=100)
        
        merged = merged.sort_values(by='friction_score', ascending=False)
        return Response(merged.head(100).to_dict('records'))
