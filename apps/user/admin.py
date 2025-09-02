from profile import Profile
from django.contrib import admin
from .models import User,UserSocialAuth,CarOwnerProfile,CarModel,RepairShopProfile

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'is_active', 'is_staff', 'type')
    search_fields = ('email', 'name')
    ordering = ('email',)
    list_filter = ('is_active', 'is_staff', 'type')


@admin.register(UserSocialAuth)
class UserSocialAuthAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'provider', 'id_token', 'created_at', 'updated_at')
    search_fields = ('user__email', 'provider', 'id_token')
    list_filter = ('provider',)

@admin.register(CarOwnerProfile)
class CarOwnerProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'phone', 'location', 'created_at', 'updated_at')
    search_fields = ('user__email', 'name', 'phone', 'location')
    list_filter = ('location',)
    ordering = ('user__email',)

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'car_model', 'registration_no', 'vin', 'created_at', 'updated_at')
    search_fields = ('owner__user__email', 'car_model', 'registration_no', 'vin')
    list_filter = ('owner',)
    ordering = ('car_model',)

@admin.register(RepairShopProfile)
class RepairShopProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'shop_name', 'location')
    search_fields = ('user__username', 'shop_name', 'location')
    list_filter = ('location',)
    ordering = ('shop_name',)
