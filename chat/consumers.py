import json
from datetime import datetime

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, ChatRoom, User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Handles the WebSocket connection when a user joins a chat room.

        - Extracts the room name from the URL route.
        - Constructs a group name for the chat room based on the room name.
        - Adds the user to the channel group for broadcasting messages.
        - Accepts the WebSocket connection.
        """
        # Extract room name from the URL route

        self.room_name = self.scope['url_route']['kwargs']['room_name']

        # Create a group name for the chat room

        self.room_group_name = f'chat_{self.room_name}'

        # Add the current channel (user) to the chat room group

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        room_id = text_data_json['room_id']
        sender = text_data_json['sender']

        room = await self.get_room(room_id)
        print({
            'message': message,
            'sender': sender,
            'room': room,
            'room_id': room_id,
        })
        await self.save_message(room, sender, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
                'timestamp': str(datetime.now())
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def get_room(self, room_id):
        return ChatRoom.objects.get(id=room_id)

    @database_sync_to_async
    def save_message(self, room, sender, message):
        from django.core.exceptions import ObjectDoesNotExist
        try:
            user = User.objects.get(user_name=sender)
        except ObjectDoesNotExist:
            return

        new_message = Message(room=room, sender=user, text=message)
        new_message.save()
