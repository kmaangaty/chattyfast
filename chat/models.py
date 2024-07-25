from django.db import models


class User(models.Model):
    UID = models.TextField(max_length=256, default='0')
    name = models.TextField(max_length=256, default='0')
    user_name = models.TextField(max_length=256, default='0')
    email = models.TextField(max_length=256, default='0')
    password = models.TextField(max_length=256, default='0')
    token = models.TextField(max_length=256, default='0')

    def generate_token(self):
        import string
        import secrets
        alphabet = string.ascii_letters + string.digits
        self.token = ''.join(secrets.choice(alphabet) for _ in range(32))
        self.save()


class ChatRoom(models.Model):
    user1 = models.TextField(default='0')
    user2 = models.TextField(default='0')
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(default='0')
    timestamp = models.DateTimeField(auto_now_add=True)
