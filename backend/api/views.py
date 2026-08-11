import os
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

def get_data(table_name):
    # Fallback to local CSV if supabase is not configured
    if not SUPABASE_URL or not SUPABASE_KEY:
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', f'{table_name}.csv')
        return pd.read_csv(csv_path)
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        # Fallback to CSV if connection fails
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', f'{table_name}.csv')
        return pd.read_csv(csv_path)

@api_view(['GET'])
def get_kpis(request):
    df_emp = get_data("employees")
    df_onb = get_data("onboarding")
    df_tickets = get_data("support_tickets")
    df_tools = get_data("tool_usage")
    
    total_employees = len(df_emp)
    onboarding_completion = df_onb['training_completion_percent'].mean()
    
    # Avg tickets per new hire (assuming onboarding is new hires)
    new_hire_ids = df_onb['employee_id'].unique()
    new_hire_tickets = df_tickets[df_tickets['employee_id'].isin(new_hire_ids)]
    avg_tickets = len(new_hire_tickets) / len(new_hire_ids) if len(new_hire_ids) > 0 else 0
    
    # Avg tool active minutes
    avg_tool_minutes = df_tools['active_minutes'].mean()
    
    return Response({
        "totalEmployees": total_employees,
        "onboardingCompletion": round(onboarding_completion, 1),
        "avgTickets": round(avg_tickets, 1),
        "avgToolMinutes": round(avg_tool_minutes, 1)
    })

@api_view(['GET'])
def get_friction_correlation(request):
    df_onb = get_data("onboarding")
    df_tickets = get_data("support_tickets")
    
    # Plot training_completion_percent vs. number of support_tickets per employee
    ticket_counts = df_tickets.groupby('employee_id').size().reset_index(name='ticket_count')
    merged = pd.merge(df_onb[['employee_id', 'training_completion_percent']], ticket_counts, on='employee_id', how='left').fillna(0)
    
    data = merged.to_dict('records')
    return Response(data)

@api_view(['GET'])
def get_blockers(request):
    df_tickets = get_data("support_tickets")
    # Top Onboarding Blockers
    blockers = df_tickets['issue_type'].value_counts().reset_index()
    blockers.columns = ['issue_type', 'count']
    return Response(blockers.to_dict('records'))

@api_view(['GET'])
def get_tool_adoption(request):
    df_tools = get_data("tool_usage")
    # Tool Adoption Curve: active_minutes mapped over date by tool_name
    # Assuming 'date' is string, we'll sort it
    grouped = df_tools.groupby(['date', 'tool_name'])['active_minutes'].mean().reset_index()
    # Pivot so each date is a row and tools are columns
    pivoted = grouped.pivot(index='date', columns='tool_name', values='active_minutes').fillna(0).reset_index()
    return Response(pivoted.to_dict('records'))

@api_view(['GET'])
def get_high_friction_employees(request):
    df_emp = get_data("employees")
    df_onb = get_data("onboarding")
    df_tickets = get_data("support_tickets")
    
    ticket_stats = df_tickets.groupby('employee_id').agg(
        ticket_count=('ticket_id', 'count'),
        avg_resolution=('resolution_hours', 'mean')
    ).reset_index()
    
    merged = pd.merge(df_emp[['employee_id', 'JobRole']], df_onb[['employee_id', 'onboarding_status']], on='employee_id')
    merged = pd.merge(merged, ticket_stats, on='employee_id', how='left').fillna(0)
    
    # Sort by ticket count descending
    merged = merged.sort_values(by='ticket_count', ascending=False)
    
    # Just return top 50 for table
    return Response(merged.head(50).to_dict('records'))
