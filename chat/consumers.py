import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatConversation


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = int(self.scope['url_route']['kwargs']['conversation_id'])
        self.room_group_name = f'chat_{self.conversation_id}'
        user = self.scope['user']

        if user.is_anonymous:
            await self.close()
            return

        if not await self.user_in_conversation(user.id, self.conversation_id):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'conversation_id': self.conversation_id,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Phase 2 keeps sending messages over HTTP; WebSocket is receive-only for pushes.
        return

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message'],
            'conversation': event.get('conversation'),
        }))

    @database_sync_to_async
    def user_in_conversation(self, user_id, conversation_id):
        return ChatConversation.objects.filter(
            id=conversation_id,
            participants__id=user_id,
        ).exists()
