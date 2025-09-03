from django.db import models
from django.contrib.auth import get_user_model
from apps.user.models import RepairShopProfile
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class ShopServccess(models.Model):
    tag = models.CharField(max_length=100, null=True, blank=True)


class AppointmentRequest(models.Model):
    STATUS = (
        ('awaiting', 'Awaiting'),
        ('confirmed', 'Confirmed'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('accepted', 'Accepted'),
        ('pending', 'Pending'), 
        ('cancelled', 'Cancelled'),
    )
    car_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_appointment_requests')
    repair_shop = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointment_requests')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(choices=STATUS, max_length=100, default='awaiting')
    car_model = models.CharField(max_length=100, null=True, blank=True)
    issue = models.TextField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    star = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.car_owner.email}'s appointment request"
    

class Notification(models.Model):
    STATUS = (
        ('read', 'Read'),
        ('unread', 'Unread'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=100, default='unread')
    icon = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_age(self):
        now = timezone.now()
        time_difference = now - self.created_at
        
        if time_difference < timedelta(minutes=1):
            return "just now"
        
        elif time_difference < timedelta(hours=1):
            minutes = int(time_difference.total_seconds() // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        
        elif time_difference < timedelta(days=1):
            hours = int(time_difference.total_seconds() // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"

        else:
            days = time_difference.days
            return f"{days} day{'s' if days != 1 else ''} ago"
        
    def __str__(self):
        return f"{self.user.email}'s notification" 
    

class Review(models.Model):
    shop = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_reviews')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_reviews')
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.email}'s review" 


