from django.urls import path
from .views import CarOwnerProfileUpdateView, RepairShopOProfileUpdateView

urlpatterns = [
    path('car-owner-profile/update/', CarOwnerProfileUpdateView.as_view(), name='user_profile_update'),  
    path('repair-shop-profile/update/', RepairShopOProfileUpdateView.as_view(), name='repair_shop_profile_update'),
]
