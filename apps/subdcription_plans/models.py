from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta 

User = get_user_model()

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    saving = models.IntegerField(null=True, blank=True)
    max_scans = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}'s subdcription plan"
    
class SubscriptionFeature(models.Model):
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='features')
    context = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plan.name}'s subdcription feature"
    
    class Meta:
        ordering = ['is_active', 'created_at']
        unique_together = ('plan', 'context')

class PerchanceSubscription(models.Model):
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='perchance_subs')
    shop = models.ForeignKey(User, on_delete=models.CASCADE, related_name='perchance_subs')
    is_active = models.BooleanField(default=False)
    scan_count = models.IntegerField(null=True, blank=True)
    available_scans = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def expired(self):
        return self.created_at + timedelta(days=30) < datetime.now()
    
    def available_days(self):
        return 30 - (datetime.now() - self.created_at).days

