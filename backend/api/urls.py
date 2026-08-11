from django.urls import path
from . import views

urlpatterns = [
    path('kpis/', views.DashboardKPIsView.as_view(), name='dashboard_kpis'),
    path('charts/', views.FrictionChartsView.as_view(), name='friction_charts'),
    path('employees/', views.EmployeeFrictionTableView.as_view(), name='employee_friction'),
]
