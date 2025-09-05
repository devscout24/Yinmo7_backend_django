from django.contrib import admin
from .models import AppointmentRequest,Notification,Review

# Register your models here.
@admin.register(AppointmentRequest)
class AppointmentRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'car_owner', 'repair_shop', 'date', 'time', 'status', 'car_model', 'issue', 'created_at', 'updated_at')
    search_fields = ('car_owner__email', 'repair_shop__email', 'car_model', 'issue')
    list_filter = ('status',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'message', 'status', 'icon', 'created_at', 'updated_at')
    search_fields = ('user__email', 'title', 'message', 'icon')
    list_filter = ('status',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'owner', 'review', 'star', 'rating', 'total_reviews', 'total_stars', 'created_at', 'updated_at')
    search_fields = ('shop__email', 'owner__email', 'review')
    list_filter = ('rating',)
