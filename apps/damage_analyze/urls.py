from django.urls import path

from apps.damage_analyze.views import CreateBookingView, CreateReviewView, DamageAnalysisView, DeleteItemsFromEstimateList, ListOfCarOwnerBooking, ShowEstimateList

urlpatterns = [
    path('analyze-damage/', DamageAnalysisView.as_view(), name='analyze_damage'),
    path('estimate-list/', ShowEstimateList.as_view(), name='estimate_list'),
    path('delete-estimate-items/', DeleteItemsFromEstimateList.as_view(), name='delete_estimate_items'),
    path('create-booking/', CreateBookingView.as_view(), name='create_booking'),
    path('booking-list/', ListOfCarOwnerBooking.as_view(), name='list_bookings'),
    path('create-review/<int:shop_id>/', CreateReviewView.as_view(), name='create_review'),


]