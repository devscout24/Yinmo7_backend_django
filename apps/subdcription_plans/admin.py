from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, PerchanceSubscription, SubscriptionFeature

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'max_scans', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'is_active')
    search_fields = ('user__username', 'plan__name')
    list_filter = ('is_active',)

@admin.register(PerchanceSubscription)
class PerchanceSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'plan', 'is_active', 'scan_count', 'available_scans', 'created_at', 'updated_at')
    search_fields = ('shop__username', 'plan__name')
    list_filter = ('is_active',)

@admin.register(SubscriptionFeature)
class SubscriptionFeatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'context', 'is_active', 'created_at', 'updated_at')
    search_fields = ('plan__name', 'context')
    list_filter = ('is_active',)
