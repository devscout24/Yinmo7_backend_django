from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth import authenticate
from dj_rest_auth.registration.serializers import SocialLoginSerializer

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('full_name','email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

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