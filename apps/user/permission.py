from rest_framework import permissions
from apps.repair_shop.models import AppointmentRequest
from rest_framework.permissions import BasePermission

class IsCarOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'type', None) == 'car_owner'

class IsRepairShop(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'type', None) == 'repair_shop'
    
class IsShopOwner(BasePermission):
    def has_permission(self, request, view):
        return AppointmentRequest.objects.filter(repair_shop=request.user).exists()