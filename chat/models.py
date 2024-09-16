from django.db import models


from django.db import models
import string
import secrets


class User(models.Model):
    """
    Represents a user in the system.

    Attributes:
        UID (TextField): Unique identifier for the user.
        name (TextField): The real name of the user.
        user_name (TextField): The username of the user.
        email (TextField): The email address of the user.
        password (TextField): The password of the user (preferably hashed).
        token (TextField): Authentication token for the user.

    Methods:
        generate_token: Generates a new authentication token for the user and saves it.
    """
    UID = models.TextField(max_length=256, default='0')
    name = models.TextField(max_length=256, default='0')
    user_name = models.TextField(max_length=256, default='0')
    email = models.TextField(max_length=256, default='0')
    password = models.TextField(max_length=256, default='0')
    token = models.TextField(max_length=256, default='0')

    def generate_token(self):
        """
        Generates a new authentication token for the user and updates the `token` field.

        The token is a 32-character string consisting of random ASCII letters and digits.
        The new token is saved to the database.
        """
        alphabet = string.ascii_letters + string.digits
        self.token = ''.join(secrets.choice(alphabet) for _ in range(32))
        self.save()


class ChatRoom(models.Model):
    """
    Represents a chat room between two users.

    Attributes:
        user1 (TextField): The username of the first participant.
        user2 (TextField): The username of the second participant.
        created_at (DateTimeField): The timestamp when the chat room was created. Automatically set when the room is created.
    """
    user1 = models.TextField(default='0')
    user2 = models.TextField(default='0')
    encryption_key = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    """
    Represents a message sent within a chat room.

    Attributes:
        room (ForeignKey): The chat room in which the message was sent.
                           Links to the `ChatRoom` model.
        sender (ForeignKey): The user who sent the message.
                             Links to the `User` model.
        text (TextField): The content of the message.
        timestamp (DateTimeField): The time when the message was created. Automatically set when the message is created.
    """
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(default='0')
    timestamp = models.DateTimeField(auto_now_add=True)
