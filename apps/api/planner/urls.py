"""
Planner URL Configuration
"""

from django.urls import path
from .views import (
    GeneratePlanView,
    PlanDetailView,
    PlanCreateView,
    HealthCheckView,
)

urlpatterns = [
    path('generate/', GeneratePlanView.as_view(), name='generate-plan'),
    path('plans/', PlanCreateView.as_view(), name='create-plan'),
    path('plans/<str:plan_id>/', PlanDetailView.as_view(), name='plan-detail'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]
