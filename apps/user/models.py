from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin



class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError ("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)
    

class User(AbstractBaseUser,PermissionsMixin):
    USER_TYPES = (
        ('car_owner', 'Car Owner'),
        ('repair_shop', 'Repair Shop'),
        ('insurances_provider', 'Insurance Provider'),
        ('repair_shop_employee', 'Repair Shop Employee'),
    )
    email = models.EmailField(unique=True)
    apple_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    google_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    name = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(choices=USER_TYPES, max_length=100,null=False, blank=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
    

class UserOtp(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    token = models.CharField(max_length=255,unique=True)
    otp = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserSocialAuth(models.Model):
    PROVIDER =(
        ('apple', 'Apple'),
        ('google', 'Google'),
    )
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='social_auth')
    id_token = models.CharField(max_length=100, null=True, blank=True)
    provider = models.CharField(choices=PROVIDER, max_length=100, default='google')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CarOwnerProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, null=True,blank=True, related_name='car_owner')
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='car_owner_profile_image', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.user.name = self.name
        super(CarOwnerProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email}'s car owner profile name is {self.name}"
    
class CarModel(models.Model):
    owner = models.ForeignKey(CarOwnerProfile,on_delete=models.CASCADE, related_name='car_models')
    car_model = models.CharField(max_length=100, null=True, blank=True)
    registration_no = models.CharField(max_length=100, null=True, blank=True)
    vin = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): 
        return f"{self.owner.name }'s car model is {self.car_model}"



class RepairShopProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='repair_shop')
    shop_name = models.CharField(max_length=100, null=True, blank=True)
    contact_person_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    logo = models.FileField(upload_to='repair_shop_profile_image', null=True, blank=True)
    cover_image = models.FileField(upload_to='repair_shop_cover_image', null=True, blank=True)
    charge_range = models.CharField(max_length=100, null=True, blank=True)

    
   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    @property
    def calculated_rating(self):
        if self.total_reviews > 0:
            return self.total_stars / self.total_reviews
        return None

    def save(self, *args, **kwargs):
        if self.shop_name:
            self.user.name = self.shop_name
        super(RepairShopProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email}'s repair shop name is {self.shop_name} contact person name is {self.contact_person_name}"


class RepairShopImage(models.Model):
    shop = models.ForeignKey(RepairShopProfile, on_delete=models.CASCADE, related_name='cover_images')
    image = models.ImageField(upload_to='repair_shop_cover_image')



class RepairShopImage(models.Model):
    shop = models.ForeignKey(RepairShopProfile, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='repair_shop_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shop.user.email}'s repair shop image"
    

class RepairshopBesinessHour(models.Model):
    DAYS_OF_WEEK = [
    ('Sunday', 'Sunday'),
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
]
    shop = models.ForeignKey(RepairShopProfile, on_delete=models.CASCADE, related_name='business_hours')
    day = models.CharField(max_length=100, null=True, blank=True, choices=DAYS_OF_WEEK)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shop.user.email}'s repair shop business hours"
    

class InsuranceProviderProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='insurance_provider')
    insurance_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.insurance_name:
            self.user.name = self.insurance_name
        super(InsuranceProviderProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email}'s insurance provider name is {self.insurance_name}"



    

                       