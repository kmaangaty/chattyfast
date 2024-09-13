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
        """
        Handles WebSocket disconnection.

        - Removes the user from the chat room group when they disconnect.

        Args:
            close_code (int): The WebSocket close code indicating why the connection was closed.
        """
        # Remove the current channel from the chat room group
        await self.channel_layer.group_discard(
            self.room_group_name,  # The group name for the chat room
            self.channel_name  # The specific WebSocket connection/channel
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
        # Parse the JSON data from the WebSocket message
        text_data_json = json.loads(text_data)
        message = text_data_json['message']  # Extract the message content
        room_id = text_data_json['room_id']  # Extract the room ID
        sender = text_data_json['sender']    # Extract the sender's username

        # Retrieve the chat room object asynchronously using its ID
        room = await self.get_room(room_id)

        # Debugging: Print the received message details (optional, for development)
        print({
            'message': message,
            'sender': sender,
            'room': room,
            'room_id': room_id,
        })

        # Save the message to the database (message storage logic needs to be implemented in save_message)
        await self.save_message(room, sender, message)

        # Broadcast the message to all members of the chat room group
        await self.channel_layer.group_send(
            self.room_group_name,  # The name of the group for the chat room
            {
                'type': 'chat_message',  # Event type for handling the chat message
                'message': message,      # The content of the message
                'sender': sender,        # The sender's username
                'timestamp': str(datetime.now())  # Timestamp of when the message was sent
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
        # Extract the message content, sender, and timestamp from the event
        message = event['message']     # The message content to be sent
        sender = event['sender']       # The username of the sender
        timestamp = event['timestamp'] # The time when the message was sent

        # Send the message to the WebSocket client in JSON format
        await self.send(text_data=json.dumps({
            'message': message,       # Include the message in the response
            'sender': sender,         # Include the sender's username
            'timestamp': timestamp    # Include the message's timestamp
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
