# urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('search_user/', views.search_user, name='search_user'),
    path('chat/<int:user_id>/', views.chat_room, name='chat_room'),
    path('get_room_messages/<int:room_id>/', views.get_room_messages, name='get_room_messages'),
    path('get_user_chat_rooms', views.get_user_chat_rooms, name='get_user_chat_rooms'),

]