from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth import authenticate
from dj_rest_auth.registration.serializers import SocialLoginSerializer

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=User.USER_TYPES)
    shop_name = serializers.CharField(required=False, allow_blank=True)
    contact_person_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    shop_address = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = User
        fields = ('name', 'email', 'password', 'confirm_password', 'type', 'shop_name', 'contact_person_name', 'phone', 'shop_address')
    
    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        shop_name = validated_data.pop('shop_name', None)
        contact_person_name = validated_data.pop('contact_person_name', None)
        phone = validated_data.pop('phone', None)
        shop_address = validated_data.pop('shop_address', None)
        user = User.objects.create_user(**validated_data)
        if user.type == 'repair_shop':
            from apps.user.models import RepairShopProfile
            profile, created = RepairShopProfile.objects.get_or_create(
                user=user,
                defaults={
                    'shop_name': shop_name,
                    'contact_person_name': contact_person_name,
                    'phone': phone,
                    'location': shop_address
                }
            )
            if not created:
                if shop_name is not None:
                    profile.shop_name = shop_name
                if contact_person_name is not None:
                    profile.contact_person_name = contact_person_name
                if phone is not None:
                    profile.phone = phone
                if shop_address is not None:
                    profile.location = shop_address
                profile.save()
        return user

class SigninSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return {'user':user}
    

class AppleLoginSerializer(SocialLoginSerializer):
    id_token = serializers.CharField(required=True)

    def validate(self, attrs):
        id_token = attrs.get("id_token")
        if not id_token:
            raise serializers.ValidationError({"id_token": "This field is required."})
        attrs["access_token"] = id_token
        return super().validate(attrs)

class GoogleLoginSerializer(SocialLoginSerializer):
    id_token = serializers.CharField(required=True)

    def validate(self, attrs):
        id_token = attrs.get("id_token")
        if not id_token:
            raise serializers.ValidationError({"id_token": "This field is required."})
        attrs["access_token"] = id_token
        return super().validate(attrs)