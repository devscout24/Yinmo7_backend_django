from rest_framework import serializers
from apps.repair_shop.models import BookingRequest

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        fields = '__all__'