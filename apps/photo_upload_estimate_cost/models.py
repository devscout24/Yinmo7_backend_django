from django.db import models
from apps.user.models import User,CarModel,RepairShopProfile

class RepairRequest(models.Model):
    car = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='repair_requests')
    shop = models.ForeignKey(RepairShopProfile, on_delete=models.CASCADE, related_name='repair_requests', null=True, blank=True)
    photo = models.ImageField(upload_to='repair_photos/')
    booking_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Repair for {self.car}"

class DamagePart(models.Model):
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='damage_parts')
    component_name = models.CharField(max_length=100)
    damage_description = models.CharField(max_length=100, blank=True)
    action_required = models.TextField()
    estimated_cost_min = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_cost_max = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.part_name} - {self.repair_request}"
    

class Booking(models.Model):
    CHOICE_OPTIONS = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='bookings')
    shop = models.ForeignKey(RepairShopProfile, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    booking_date = models.DateTimeField(null=True, blank=True)
    choice = models.CharField(max_length=10, choices=CHOICE_OPTIONS, default='Pending')
    review = models.TextField(null=True, blank=True)
    star_rating = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
