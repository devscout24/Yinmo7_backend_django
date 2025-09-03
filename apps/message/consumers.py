# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Conversation, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']

        if self.user.is_anonymous:
            await self.close()
        else:
            if await self.is_participant():
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
                await self.mark_messages_as_read()
            else:
                await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_content = text_data_json.get('message')
            message_type = text_data_json.get('type', 'chat_message')

            if message_type == 'chat_message' and message_content:
                saved_message = await self.save_message(message_content)
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_id': str(saved_message.id),
                        'message': saved_message.message,
                        'sender_id': self.user.id,
                        'sender_email': self.user.email,
                        'timestamp': saved_message.created_at.isoformat(),
                        'read': saved_message.read,
                    }
                )
            elif message_type == 'read_receipt':
                await self.mark_messages_as_read()

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON'}))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_email': event['sender_email'],
            'timestamp': event['timestamp'],
            'read': event['read'],
        }))

    @database_sync_to_async
    def save_message(self, message_content):
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            message=message_content
        )
        return message

    @database_sync_to_async
    def is_participant(self):
        return Conversation.objects.filter(
            id=self.conversation_id
        ).filter(
            Q(car_owner=self.user) | Q(repair_shop=self.user)
        ).exists()

    @database_sync_to_async
    def mark_messages_as_read(self):
        Message.objects.filter(
            conversation_id=self.conversation_id,
            read=False
        ).exclude(sender=self.user).update(read=True)