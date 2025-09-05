from .models import User, CarOwnerProfile, CarModel
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CarModel
User = get_user_model()
class CarModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        fields = ['car_model', 'registration_no', 'vin']

class CarOwnerProfileSerializer(serializers.ModelSerializer):
    car_models = CarModelSerializer(many=True)
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = CarOwnerProfile
        fields = ['name', 'phone', 'location', 'image', 'car_models']

    def update(self, instance, validated_data):
        car_models_data = validated_data.pop('car_models', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.car_models.all().delete()
        for car_data in car_models_data:
            CarModel.objects.create(owner=instance, **car_data)
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    car_owner = CarOwnerProfileSerializer()
    class Meta:
        model = User
        fields = ['id', 'email', 'type', 'car_owner']

    def update(self, instance, validated_data):
        car_owner_data = validated_data.pop('car_owner', None)
        if car_owner_data:
            car_owner, created = CarOwnerProfile.objects.get_or_create(user=instance)
            CarOwnerProfileSerializer().update(car_owner, car_owner_data)
        return super().update(instance, validated_data)


