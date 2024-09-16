import json
from datetime import datetime

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

import crypto.crypt
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

        self.room_name = self.scope['url_route']['kwargs']['room_name']

        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.

        - Removes the user from the chat room group when they disconnect.

        Args:
            close_code (int): The WebSocket close code indicating why the connection was closed.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Handles receiving messages via WebSocket.

        This method is triggered when a message is received from a WebSocket connection.
        It performs the following tasks:
        1. Parses the incoming JSON data to extract the message, room ID, and sender.
        2. Retrieves the chat room corresponding to the room ID.
        3. Saves the received message in the database.
        4. Broadcasts the message to all participants in the chat room.

        Args:
            text_data (str): The JSON-formatted message received from the WebSocket client.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        room_id = text_data_json['room_id']
        sender = text_data_json['sender']

        room = await self.get_room(room_id)
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
        """
        Handles broadcasting a message to the WebSocket client.

        This method is triggered when a message is sent to the room group via `group_send`.
        It sends the message to the WebSocket client that triggered this method.

        Args:
            event (dict): The event dictionary containing the following keys:
                - 'message': The content of the message being broadcast.
                - 'sender': The username of the sender.
                - 'timestamp': The time the message was sent.
        """

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
        """
        Retrieves the chat room from the database by its ID.

        This method is decorated with `@database_sync_to_async` to ensure that
        the database query runs asynchronously, preventing blocking of the event loop.

        Args:
            room_id (int): The ID of the chat room to be retrieved.

        Returns:
            ChatRoom: The chat room instance that matches the given room_id.

        Raises:
            ChatRoom.DoesNotExist: If no chat room with the provided ID is found.
        """
        return ChatRoom.objects.get(id=room_id)

    @database_sync_to_async
    def save_message(self, room, sender, message):
        """
        Saves a new message to the database.

        This method retrieves the user by their username (sender) and creates a new
        message linked to the specified chat room. The message is saved to the `Message` model.

        Args:
            room (ChatRoom): The chat room where the message is being sent.
            sender (str): The username of the sender of the message.
            message (str): The text content of the message to be saved.

        Returns:
            None: If the sender does not exist or the message fails to save.
        """
        from django.core.exceptions import ObjectDoesNotExist

        try:
            user = User.objects.get(user_name=sender)
        except ObjectDoesNotExist:
            return

        new_message = Message(room=room, sender=user, text=crypto.crypt.encrypt(message))
        new_message.save()
