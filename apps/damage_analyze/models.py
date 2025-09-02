from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

User = get_user_model()

class DamageAnalyze(models.Model):
    car_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyzes', null=True, blank=True)
    car_brand = models.CharField(max_length=100, null=True, blank=True)
    car_model = models.CharField(max_length=100, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='images/analyzes', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_estimated_min = models.CharField(max_length=100, null=True, blank=True)
    total_estimated_max = models.CharField(max_length=100, null=True, blank=True)
    severity = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.car_owner.email}'s analyze"

class Damage(models.Model):
    analyze = models.ForeignKey(DamageAnalyze, on_delete=models.CASCADE, related_name='damages')
    part_name = models.CharField(max_length=100, null=True, blank=True)
    damage_type = models.CharField(max_length=100, null=True, blank=True)
    damage = models.CharField(max_length=100, null=True, blank=True)
    action = models.TextField(null=True, blank=True)
    estimated_cost_min = models.CharField(max_length=100, null=True, blank=True)
    estimated_cost_max = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.analyze.car_owner.email}'s damage"
    

class HumanAnalysis(models.Model):
    analyze = models.ForeignKey(DamageAnalyze, on_delete=models.CASCADE, related_name='humans')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.analyze.car_owner.email}'s human analysis"