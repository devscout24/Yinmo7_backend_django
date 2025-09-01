from django.urls import path

from apps.photo_upload_estimate_cost.views import OpenAIService

urlpatterns = [
    path('analyze-car-damage/', OpenAIService.as_view(), name='analyze_car_damage'),
]
