from django.urls import path

from apps.damage_analyze.views import CreateBookingView, CreateReviewView, DamageAnalysisView, DeleteItemsFromEstimateList, ShowEstimateList

urlpatterns = [
    path('analyze-damage/', DamageAnalysisView.as_view(), name='analyze_damage'),
    path('estimate-list/', ShowEstimateList.as_view(), name='estimate_list'),
    path('delete-estimate-items/', DeleteItemsFromEstimateList.as_view(), name='delete_estimate_items'),
    path('create-booking/', CreateBookingView.as_view(), name='create_booking'),
    path('create-review/', CreateReviewView.as_view(), name='create_review'),


]