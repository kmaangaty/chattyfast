from django.urls import re_path
from . import consumers

# Define WebSocket URL patterns for chat rooms
websocket_urlpatterns = [
    # The `re_path` uses a regular expression to capture the room name from the URL
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
