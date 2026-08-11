from django.urls import path
from . import views

urlpatterns = [
    path('kpis/', views.get_kpis),
    path('friction-correlation/', views.get_friction_correlation),
    path('blockers/', views.get_blockers),
    path('tool-adoption/', views.get_tool_adoption),
    path('high-friction-employees/', views.get_high_friction_employees),
]
