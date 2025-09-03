from rest_framework import serializers
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'message', 'created_at', 'read', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'sender']

class ConversationSerializer(serializers.ModelSerializer):
    car_owner = UserSerializer(read_only=True)
    repair_shop = UserSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'car_owner', 'repair_shop', 'created_at', 'updated_at', 'messages', 'unread_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(read=False).exclude(sender=user).count()

class CreateConversationSerializer(serializers.ModelSerializer):
    repair_shop_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Conversation
        fields = ['repair_shop_id']
    
    def validate_repair_shop_id(self, value):
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Repair shop not found")
        return value