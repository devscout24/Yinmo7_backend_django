from django.urls import path

from apps.damage_analyze.views import DamageAnalysisView
from apps.damage_analyze.services.data_analysis import OpenAIService

urlpatterns = [
    path('analyze-damage/', DamageAnalysisView.as_view(), name='analyze_damage'),
    path('result/', OpenAIService.as_view(), name='print_settings'),    
]