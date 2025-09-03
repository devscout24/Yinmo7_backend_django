from rest_framework import serializers
from apps.repair_shop.models import AppointmentRequest
from apps.user.models import RepairShopProfile
from .models import Damage, DamageAnalyze



class AppointmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentRequest
        fields = '__all__'
        extra_kwargs = {
            'review': {'required': True},
            'star': {'required': True}
        }

    def create(self, validated_data):
        appointment = super().create(validated_data)
        user = self.context['request'].user
        star = validated_data.get('star', 0)
        from django.db.models import F
        RepairShopProfile.objects.filter(user=user).update(
            total_reviews=F('total_reviews') + 1,
            total_stars=F('total_stars') + star
        )
        return appointment

class RepairShopProfileSerializer(serializers.Serializer):
    class Meta:
        model = RepairShopProfile
        fields = '__all__'


class DamageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Damage
        fields = ['id','part_name','damage_type','damage','action','estimated_cost_min','estimated_cost_max','created_at','updated_at']

class DamageAnalyzeSerializer(serializers.ModelSerializer):
    damages = DamageSerializer(many=True, read_only=True)  

    class Meta:
        model = DamageAnalyze
        fields = ['id','car_brand','car_model','year','image','total_estimated_min','total_estimated_max','severity','created_at','updated_at','damages']