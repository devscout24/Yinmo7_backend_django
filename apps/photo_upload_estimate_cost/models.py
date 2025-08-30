from django.db import models
from apps.user.models import User

# Create your models here.
class Car(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    vin = models.CharField(max_length=17, unique=True)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100, null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.color})"


class RepairRequest(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='repair_requests')
    shop = models.ForeignKey(RepairShop, on_delete=models.CASCADE, related_name='repair_requests', null=True, blank=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='repair_photos/')
    estimated_cost_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estimated_cost_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ai_analysis = models.JSONField(blank=True, null=True)  # Store OpenAI analysis results
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Repair for {self.car}"

class DamagePart(models.Model):
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='damage_parts')
    part_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    damage_description = models.TextField()
    action_required = models.TextField()
    estimated_cost_min = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_cost_max = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.part_name} - {self.repair_request}"
