from django.db import models

from project import settings

# Create your models here.
class Car_Owner_dashboard(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_repairs = models.IntegerField(default=0)
    active_bookings = models.IntegerField(default=0)
    last_estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_shop_bookings = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email
    

class Repair_Shop_dashboard(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_leads = models.IntegerField(default=0)
    new_estimates_requests = models.IntegerField(default=0)
    todays_appointments = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email

class Analytics_Tab(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    request_this_month = models.IntegerField(default=0)
    avg_response_time = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    new_customers = models.IntegerField(default=0)
    returns = models.IntegerField(default=0)

    def __str__(self):
        return self.user.email
