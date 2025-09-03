# views.py
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, 
    MessageSerializer, 
    CreateConversationSerializer,
    UserSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateConversationSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        # CORRECT: Single filter with Q objects using OR condition
        return Conversation.objects.filter(
            Q(car_owner=self.request.user) | Q(repair_shop=self.request.user)
        ).prefetch_related('messages').order_by('-updated_at')
    
    def perform_create(self, serializer):
        repair_shop_id = self.request.data.get('repair_shop_id')
        repair_shop = User.objects.get(id=repair_shop_id)
        
        # Check if conversation already exists using Q objects
        conversation, created = Conversation.objects.filter(
            Q(car_owner=self.request.user) & Q(repair_shop=repair_shop)
        ).get_or_create(
            defaults={'car_owner': self.request.user, 'repair_shop': repair_shop}
        )
        
        if not created:
            serializer.instance = conversation
        else:
            serializer.instance = conversation

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        
        # CORRECT: Single filter with Q objects
        conversation_exists = Conversation.objects.filter(
            id=conversation_id
        ).filter(
            Q(car_owner=self.request.user) | Q(repair_shop=self.request.user)
        ).exists()
        
        if not conversation_exists:
            raise PermissionDenied("You don't have access to this conversation")
        
        return Message.objects.filter(
            conversation_id=conversation_id
        ).select_related('sender', 'conversation').order_by('created_at')
    
    def perform_create(self, serializer):
        conversation_id = self.kwargs['conversation_id']
        
        # CORRECT: Using get() with Q objects
        conversation = get_object_or_404(
            Conversation,
            Q(id=conversation_id) & 
            (Q(car_owner=self.request.user) | Q(repair_shop=self.request.user))
        )
        
        serializer.save(conversation=conversation, sender=self.request.user)