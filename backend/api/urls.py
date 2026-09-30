from django.urls import path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(openapi.Info(title="API", default_version='v1'), public=True, permission_classes=(permissions.AllowAny,))

urlpatterns = [
    path('kpis/', views.DashboardKPIsView.as_view(), name='dashboard_kpis'),
    path('charts/', views.FrictionChartsView.as_view(), name='friction_charts'),
    path('employees/', views.EmployeeFrictionTableView.as_view(), name='employee_friction'),
    path('employees/<int:employee_id>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

