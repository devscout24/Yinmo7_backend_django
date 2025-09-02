from django.contrib import admin
from .models import Message, Conversation

# Register your models here.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'receiver', 'message', 'created_at', 'updated_at')
    search_fields = ('sender__email', 'receiver__email', 'message')
    list_filter = ('created_at', 'updated_at')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'car_owner', 'repair_shop', 'created_at', 'updated_at')
    search_fields = ('car_owner__email', 'repair_shop__email')
    list_filter = ('created_at', 'updated_at')
