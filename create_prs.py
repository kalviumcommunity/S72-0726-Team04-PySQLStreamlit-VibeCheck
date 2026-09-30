import os
import subprocess

REPO_DIR = r'c:\Users\v4paw\Desktop\vibe\S72-0726-Team04-PySQLStreamlit-VibeCheck'
os.chdir(REPO_DIR)

changes = [
    {
        'branch': 'vedant/feat-caching-kpis',
        'file': 'backend/api/views.py',
        'search': 'class DashboardKPIsView(APIView):\n    def get(self, request):',
        'replace': 'from django.utils.decorators import method_decorator\nfrom django.views.decorators.cache import cache_page\n\nclass DashboardKPIsView(APIView):\n    @method_decorator(cache_page(60 * 15))\n    def get(self, request):',
        'msg': 'Add Caching for KPI Dashboard'
    },
    {
        'branch': 'vedant/feat-pagination',
        'file': 'backend/api/views.py',
        'search': '        merged = merged.sort_values(by=\'friction_score\', ascending=False)\n        return Response(merged.head(100).to_dict(\'records\'))',
        'replace': '        merged = merged.sort_values(by=\'friction_score\', ascending=False)\n        page = int(request.GET.get(\'page\', 1))\n        limit = int(request.GET.get(\'limit\', 20))\n        start = (page - 1) * limit\n        end = start + limit\n        paginated = merged.iloc[start:end]\n        return Response({\'total\': len(merged), \'page\': page, \'data\': paginated.to_dict(\'records\')})',
        'msg': 'Implement Pagination for Employee Table'
    },
    {
        'branch': 'vedant/feat-department-filter',
        'file': 'backend/api/views.py',
        'search': '        merged = pd.merge(merged, ticket_stats, on=\'employee_id\', how=\'left\').fillna(0)\n        ml_preds = get_ml_predictions()',
        'replace': '        merged = pd.merge(merged, ticket_stats, on=\'employee_id\', how=\'left\').fillna(0)\n        department = request.GET.get(\'department\')\n        if department:\n            merged = merged[merged[\'Department\'].str.lower() == department.lower()]\n        ml_preds = get_ml_predictions()',
        'msg': 'Add Department Filtering'
    },
    {
        'branch': 'vedant/feat-export-csv',
        'file': 'backend/api/urls.py',
        'search': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n]',
        'replace': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n    path(\'employees/export/\', views.ExportEmployeesCSVView.as_view(), name=\'export_employees\'),\n]',
        'file2': 'backend/api/views.py',
        'search2': 'class EmployeeDetailView(APIView):',
        'replace2': 'from django.http import HttpResponse\nclass ExportEmployeesCSVView(APIView):\n    def get(self, request):\n        df_emp = fetch_table_as_df("employees")\n        response = HttpResponse(content_type=\'text/csv\')\n        response[\'Content-Disposition\'] = \'attachment; filename="employees.csv"\'\n        df_emp.to_csv(path_or_buf=response, index=False)\n        return response\n\nclass EmployeeDetailView(APIView):',
        'msg': 'CSV Export Endpoint for Employees'
    },
    {
        'branch': 'vedant/fix-error-handling',
        'file': 'backend/api/utils.py',
        'search': '    csv_path = os.path.join(DATA_DIR, f"{table_name}.csv")\n    if os.path.exists(csv_path):\n        return pd.read_csv(csv_path)\n    return pd.DataFrame()',
        'replace': '    try:\n        csv_path = os.path.join(DATA_DIR, f"{table_name}.csv")\n        if os.path.exists(csv_path):\n            return pd.read_csv(csv_path)\n        print(f"Warning: {table_name}.csv not found.")\n        return pd.DataFrame()\n    except Exception as e:\n        print(f"Error loading {table_name}: {e}")\n        return pd.DataFrame()',
        'msg': 'Improve Data Fetching Error Handling'
    },
    {
        'branch': 'vedant/feat-health-check',
        'file': 'backend/api/urls.py',
        'search': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n]',
        'replace': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n    path(\'health/\', views.HealthCheckView.as_view(), name=\'health_check\'),\n]',
        'file2': 'backend/api/views.py',
        'search2': '        return Response(detail)\n',
        'replace2': '        return Response(detail)\n\nclass HealthCheckView(APIView):\n    def get(self, request):\n        return Response({"status": "ok", "version": "1.0.0"})\n',
        'msg': 'Add Health Check Endpoint'
    },
    {
        'branch': 'vedant/feat-swagger-docs',
        'file': 'backend/api/urls.py',
        'search': 'from . import views\n\nurlpatterns = [',
        'replace': 'from . import views\nfrom rest_framework import permissions\nfrom drf_yasg.views import get_schema_view\nfrom drf_yasg import openapi\n\nschema_view = get_schema_view(openapi.Info(title="API", default_version=\'v1\'), public=True, permission_classes=(permissions.AllowAny,))\n\nurlpatterns = [',
        'file2': 'backend/api/urls.py',
        'search2': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n]',
        'replace2': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n    path(\'swagger/\', schema_view.with_ui(\'swagger\', cache_timeout=0), name=\'schema-swagger-ui\'),\n]',
        'msg': 'Setup Swagger API Documentation'
    },
    {
        'branch': 'vedant/feat-cors-config',
        'file': 'backend/config/settings.py',
        'search': '    \'api\',\n]',
        'replace': '    \'api\',\n    \'corsheaders\',\n]',
        'file2': 'backend/config/settings.py',
        'search2': 'MIDDLEWARE = [\n    \'django.middleware.security.SecurityMiddleware\',',
        'replace2': 'MIDDLEWARE = [\n    \'corsheaders.middleware.CorsMiddleware\',\n    \'django.middleware.security.SecurityMiddleware\',',
        'msg': 'Configure CORS Headers'
    },
    {
        'branch': 'vedant/feat-search-employee',
        'file': 'backend/api/views.py',
        'search': '        merged = pd.merge(merged, ticket_stats, on=\'employee_id\', how=\'left\').fillna(0)\n        ml_preds = get_ml_predictions()',
        'replace': '        merged = pd.merge(merged, ticket_stats, on=\'employee_id\', how=\'left\').fillna(0)\n        search = request.GET.get(\'search\')\n        if search:\n            merged = merged[merged[\'JobRole\'].str.contains(search, case=False, na=False)]\n        ml_preds = get_ml_predictions()',
        'msg': 'Add Employee Search Functionality'
    },
    {
        'branch': 'vedant/feat-dynamic-sorting',
        'file': 'backend/api/views.py',
        'search': '        merged = merged.sort_values(by=\'friction_score\', ascending=False)\n        return Response(merged.head(100).to_dict(\'records\'))',
        'replace': '        sort_by = request.GET.get(\'sort_by\', \'friction_score\')\n        sort_desc = request.GET.get(\'sort_desc\', \'true\').lower() == \'true\'\n        if sort_by in merged.columns:\n            merged = merged.sort_values(by=sort_by, ascending=not sort_desc)\n        else:\n            merged = merged.sort_values(by=\'friction_score\', ascending=False)\n        return Response(merged.head(100).to_dict(\'records\'))',
        'msg': 'Dynamic Sorting for Friction Table'
    },
    {
        'branch': 'vedant/feat-configurable-weights',
        'file': 'backend/api/views.py',
        'search': '        # Calculate friction_score: (Ticket Count * 10) + (Avg Resolution Hours * 2) - (Training % * 0.5)\n        merged[\'friction_score\'] = (merged[\'ticket_count\'] * 10) + (merged[\'avg_resolution\'] * 2) - (merged[\'training_completion_percent\'] * 0.5)',
        'replace': '        t_w = float(os.getenv(\'FRICTION_TICKET_WEIGHT\', 10.0))\n        r_w = float(os.getenv(\'FRICTION_RES_WEIGHT\', 2.0))\n        tr_w = float(os.getenv(\'FRICTION_TRAIN_WEIGHT\', 0.5))\n        merged[\'friction_score\'] = (merged[\'ticket_count\'] * t_w) + (merged[\'avg_resolution\'] * r_w) - (merged[\'training_completion_percent\'] * tr_w)',
        'msg': 'Configurable Friction Score Weights'
    },
    {
        'branch': 'vedant/feat-date-range-filter',
        'file': 'backend/api/views.py',
        'search': '        df_onb = fetch_table_as_df("onboarding")\n        df_tickets = fetch_table_as_df("support_tickets")\n        \n        onb_days_clean',
        'replace': '        df_onb = fetch_table_as_df("onboarding")\n        df_tickets = fetch_table_as_df("support_tickets")\n        \n        start_date = request.GET.get(\'start_date\')\n        end_date = request.GET.get(\'end_date\')\n        if start_date and end_date and \'start_date\' in df_onb.columns:\n            df_onb = df_onb[(df_onb[\'start_date\'] >= start_date) & (df_onb[\'start_date\'] <= end_date)]\n            \n        onb_days_clean',
        'msg': 'Date Range Filtering for KPIs'
    },
    {
        'branch': 'vedant/feat-tool-usage-agg',
        'file': 'backend/api/urls.py',
        'search': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n]',
        'replace': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n    path(\'tools/usage/\', views.ToolUsageAggView.as_view(), name=\'tool_usage_agg\'),\n]',
        'file2': 'backend/api/views.py',
        'search2': '        return Response(detail)\n',
        'replace2': '        return Response(detail)\n\nclass ToolUsageAggView(APIView):\n    def get(self, request):\n        df = fetch_table_as_df("tool_usage")\n        if df.empty: return Response([])\n        agg = df.groupby(\'tool_name\')[\'active_minutes\'].sum().reset_index()\n        return Response(agg.to_dict(\'records\'))\n',
        'msg': 'Tool Usage Aggregation Endpoint'
    },
    {
        'branch': 'vedant/feat-buddy-stats',
        'file': 'backend/api/urls.py',
        'search': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n]',
        'replace': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n    path(\'stats/buddies/\', views.BuddyStatsView.as_view(), name=\'buddy_stats\'),\n]',
        'file2': 'backend/api/views.py',
        'search2': '        return Response(detail)\n',
        'replace2': '        return Response(detail)\n\nclass BuddyStatsView(APIView):\n    def get(self, request):\n        df = fetch_table_as_df("onboarding")\n        if df.empty: return Response({})\n        impact = df.groupby(\'buddy_assigned\').agg(avg_training=(\'training_completion_percent\', \'mean\'), count=(\'employee_id\', \'count\')).reset_index()\n        return Response(impact.to_dict(\'records\'))\n',
        'msg': 'Buddy Impact Analysis Endpoint'
    },
    {
        'branch': 'vedant/feat-ml-fallback-logs',
        'file': 'backend/api/views.py',
        'search': 'import os\nimport pickle',
        'replace': 'import os\nimport pickle\nimport logging\nlogger = logging.getLogger(__name__)',
        'file2': 'backend/api/views.py',
        'search2': '        print(f"Notice: Standard ML model predict_proba skipped ({e}), utilizing risk scores dataset.")',
        'replace2': '        logger.warning(f"ML model execution failed: {e}. Falling back to CSV.")',
        'msg': 'ML Model Fallback Logging'
    },
    {
        'branch': 'vedant/feat-high-risk-flags',
        'file': 'backend/api/views.py',
        'search': '            "predicted_risk": float(round(predicted_risk, 1)),\n            "tickets": tickets_list,',
        'replace': '            "predicted_risk": float(round(predicted_risk, 1)),\n            "high_risk_flag": bool(predicted_risk > 90.0 or friction_score > 85.0),\n            "tickets": tickets_list,',
        'msg': 'Flag High-Risk Employees'
    },
    {
        'branch': 'vedant/feat-api-throttling',
        'file': 'backend/config/settings.py',
        'search': 'USE_TZ = True\n\n\n# Static files',
        'replace': 'USE_TZ = True\n\nREST_FRAMEWORK = {\n    \'DEFAULT_THROTTLE_CLASSES\': [\n        \'rest_framework.throttling.AnonRateThrottle\',\n        \'rest_framework.throttling.UserRateThrottle\'\n    ],\n    \'DEFAULT_THROTTLE_RATES\': {\n        \'anon\': \'100/day\',\n        \'user\': \'1000/day\'\n    }\n}\n\n# Static files',
        'msg': 'Implement API Rate Limiting'
    },
    {
        'branch': 'vedant/feat-custom-exceptions',
        'file': 'backend/api/views.py',
        'search': '        ml_preds = get_ml_predictions()\n\n        emp_row = df_emp[df_emp[\'employee_id\'] == employee_id]',
        'replace': '        ml_preds = get_ml_predictions()\n\n        if df_emp.empty or df_onb.empty:\n            return Response({"error": "Core datasets missing"}, status=503)\n\n        emp_row = df_emp[df_emp[\'employee_id\'] == employee_id]',
        'msg': 'Custom Exception Handlers'
    },
    {
        'branch': 'vedant/feat-refresh-data',
        'file': 'backend/api/urls.py',
        'search': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n]',
        'replace': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n    path(\'system/refresh/\', views.DataRefreshView.as_view(), name=\'data_refresh\'),\n]',
        'file2': 'backend/api/views.py',
        'search2': '        return Response(detail)\n',
        'replace2': '        return Response(detail)\n\nfrom django.core.cache import cache\nclass DataRefreshView(APIView):\n    def post(self, request):\n        cache.clear()\n        return Response({"status": "success"})\n',
        'msg': 'Cache Invalidation Endpoint'
    },
    {
        'branch': 'vedant/test-kpi-view',
        'file': 'backend/api/tests.py',
        'search': '# Create your tests here.',
        'replace': 'from django.urls import reverse\nfrom rest_framework.test import APIClient\n\nclass DashboardKPIsTest(TestCase):\n    def setUp(self):\n        self.client = APIClient()\n    def test_get_kpis(self):\n        response = self.client.get(reverse(\'dashboard_kpis\'))\n        self.assertEqual(response.status_code, 200)\n        self.assertIn(\'avg_onboarding_days\', response.data)',
        'msg': 'Unit Tests for Dashboard KPIs'
    },
    {
        'branch': 'vedant/test-friction-table',
        'file': 'backend/api/tests.py',
        'search': '# Create your tests here.',
        'replace': 'from django.urls import reverse\nfrom rest_framework.test import APIClient\n\nclass EmployeeFrictionTableTest(TestCase):\n    def setUp(self):\n        self.client = APIClient()\n    def test_get_employee_table(self):\n        response = self.client.get(reverse(\'employee_friction\'))\n        self.assertEqual(response.status_code, 200)\n        self.assertIsInstance(response.data, list)',
        'msg': 'Unit Tests for Friction Table'
    },
    {
        'branch': 'vedant/feat-department-kpis',
        'file': 'backend/api/urls.py',
        'search': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n]',
        'replace': '    path(\'employees/<int:employee_id>/\', views.EmployeeDetailView.as_view(), name=\'employee_detail\'),\n    path(\'kpis/department/\', views.DepartmentKPIsView.as_view(), name=\'department_kpis\'),\n]',
        'file2': 'backend/api/views.py',
        'search2': '        return Response(detail)\n',
        'replace2': '        return Response(detail)\n\nclass DepartmentKPIsView(APIView):\n    def get(self, request):\n        df_emp = fetch_table_as_df("employees")\n        df_onb = fetch_table_as_df("onboarding")\n        if df_emp.empty or df_onb.empty: return Response([])\n        merged = pd.merge(df_emp, df_onb, on=\'employee_id\')\n        dept_kpis = merged.groupby(\'Department\')[\'training_completion_percent\'].mean().reset_index()\n        dept_kpis.columns = [\'department\', \'avg_training_percent\']\n        return Response(dept_kpis.to_dict(\'records\'))\n',
        'msg': 'Department-wise KPI Aggregation'
    },
    {
        'branch': 'vedant/feat-ticket-resolution-metrics',
        'file': 'backend/api/views.py',
        'search': '            "predicted_risk": float(round(predicted_risk, 1)),\n            "tickets": tickets_list,',
        'replace': '            "predicted_risk": float(round(predicted_risk, 1)),\n            "metrics": {"total_tickets": ticket_count, "avg_resolution_hrs": float(round(avg_res, 1))},\n            "tickets": tickets_list,',
        'msg': 'Detailed Ticket Resolution Metrics'
    },
    {
        'branch': 'vedant/feat-onboarding-status-filter',
        'file': 'backend/api/views.py',
        'search': '        merged = pd.merge(merged, ticket_stats, on=\'employee_id\', how=\'left\').fillna(0)\n        ml_preds = get_ml_predictions()',
        'replace': '        merged = pd.merge(merged, ticket_stats, on=\'employee_id\', how=\'left\').fillna(0)\n        status = request.GET.get(\'status\')\n        if status:\n            merged = merged[merged[\'onboarding_status\'].str.lower() == status.lower()]\n        ml_preds = get_ml_predictions()',
        'msg': 'Onboarding Status Filtering'
    },
    {
        'branch': 'vedant/feat-manager-view',
        'file': 'backend/api/views.py',
        'search': '        merged = pd.merge(merged, ticket_stats, on=\'employee_id\', how=\'left\').fillna(0)\n        ml_preds = get_ml_predictions()',
        'replace': '        merged = pd.merge(merged, ticket_stats, on=\'employee_id\', how=\'left\').fillna(0)\n        manager = request.GET.get(\'manager_assigned\')\n        if manager:\n            if \'manager_assigned\' in merged.columns:\n                merged = merged[merged[\'manager_assigned\'].str.lower() == manager.lower()]\n        ml_preds = get_ml_predictions()',
        'msg': 'Manager-specific Data Filtering'
    }
]

created_branches = 0
for i, change in enumerate(changes):
    subprocess.run(['git', 'checkout', '-q', 'main'])
    try:
        subprocess.run(['git', 'branch', '-D', change['branch']], capture_output=True)
    except:
        pass
        
    subprocess.run(['git', 'checkout', '-q', '-b', change['branch']])
    
    modified = False
    
    if os.path.exists(change['file']):
        with open(change['file'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        if change['search'] in content:
            new_content = content.replace(change['search'], change['replace'])
            with open(change['file'], 'w', encoding='utf-8') as f:
                f.write(new_content)
            modified = True
            
    if 'file2' in change and os.path.exists(change['file2']):
        with open(change['file2'], 'r', encoding='utf-8') as f:
            content = f.read()
            
        if change['search2'] in content:
            new_content = content.replace(change['search2'], change['replace2'])
            with open(change['file2'], 'w', encoding='utf-8') as f:
                f.write(new_content)
            modified = True
            
    if modified:
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-q', '-m', f"feat: {change['msg']}"])
        created_branches += 1
        print(f"Created branch {i+1}/25: {change['branch']}")
    else:
        print(f"Warning: Could not apply changes for {change['branch']}")
    
subprocess.run(['git', 'checkout', '-q', 'main'])
print(f'Done processing branches. Created {created_branches} branches.')
