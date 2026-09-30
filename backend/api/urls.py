from django.urls import path
from . import views

urlpatterns = [
    path('kpis/', views.DashboardKPIsView.as_view(), name='dashboard_kpis'),
    path('charts/', views.FrictionChartsView.as_view(), name='friction_charts'),
    path('employees/', views.EmployeeFrictionTableView.as_view(), name='employee_friction'),
    path('employees/<int:employee_id>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('tools/usage/', views.ToolUsageAggView.as_view(), name='tool_usage_agg'),
]

