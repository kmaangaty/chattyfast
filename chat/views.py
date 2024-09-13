import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from .forms import UserSearchForm
from .models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ChatRoom, Message


def index(request):
    """
    Handles the request for the main index page.

    - Checks if the user has an active session with a valid token.
    - If not, redirects the user to the login page.
    - If a valid session exists, retrieves the user based on the session token and renders the index page.

    Args:
        request: The HTTP request object containing metadata about the request.

    Returns:
        - If the token is missing or invalid, the user is redirected to the login page.
        - If the token is valid, the index page is rendered with user information.
    """

    # Check if the user has a session token; if not, redirect to login page
    if 'token' not in request.session:
        return redirect('/login')

    # Get the token from the session
    token = request.session['token'][0]

    try:
        # Try to retrieve the user associated with the token
        user = User.objects.get(token=token)
    except User.DoesNotExist:
        # If the token is invalid or user does not exist, redirect to login page
        return redirect('/login')

    # Prepare the context with user information to render the index page
    context = {
        'user_id': user.id,
        'user_name': user.user_name
    }

    # Render the index page with the user's information
    return render(request, 'index.html', context)


def login(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        method = request.POST.get('method')

        try:
            user_data = User.objects.get(user_name=user_name)
            user_exist = True
        except User.DoesNotExist:
            user_exist = False

        token = create_token()
        if method == 'log':
            if user_exist and password == user_data.password:
                request.session['token'] = [token]
                user_data.token = token
                user_data.save()
                return redirect('/')
            else:
                return render(request, 'login.html', {'error': 'Invalid login credentials'})
        elif method == 'reg':
            if not user_exist:
                email = request.POST.get('email')
                request.session['token'] = [create_token()]
                user_data = User.objects.create(UID=create_token(), user_name=user_name, password=password, email=email, token=token)
                return redirect('/')
            else:
                return render(request, 'login.html', {'error': 'User already exists'})

    return render(request, 'login.html')


def create_token():
    import string
    import secrets
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(32))
    return token


@login_required
def home(request):
    return render(request, 'home.html')


def get_user_chat_rooms(request):
    user = User.objects.get(token=request.session['token'][0])
    chat_rooms = ChatRoom.objects.filter(
        Q(user1=user.user_name) | Q(user2=user.user_name)
    ).prefetch_related('message_set').distinct()

    chat_room_data = []
    for room in chat_rooms:
        last_message = room.message_set.last()
        chat_room_data.append({
            'id': room.id,
            'user_name': room.user2 if room.user1 == user.user_name else room.user1,
            'last_message': last_message.text if last_message else '',
            'last_message_time': last_message.timestamp.strftime('%H:%M') if last_message else ''
        })

    return JsonResponse({'chat_rooms': chat_room_data})


def get_or_create_room(user1, user2):
    if not (isinstance(user1, User) and isinstance(user2, User)):
        raise TypeError("Expected instances of User")

    # Ensure users have valid IDs
    if user1.id is None or user2.id is None:
        raise ValueError("One or both users have invalid IDs")

    chat_room, created = ChatRoom.objects.get_or_create(
        user1=min(user1, user2, key=lambda u: u.id),
        user2=max(user1, user2, key=lambda u: u.id)
    )
    return chat_room


@login_required
def chat_room(request, user_id):
    user = get_object_or_404(User, id=user_id)
    chat_room = get_or_create_room(request.user, user)
    messages = Message.objects.filter(room=chat_room).order_by('timestamp')
    return render(request, 'index.html', {
        'room_name': chat_room.id,
        'user': user,
        'messages': messages,
    })


def search_user(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = UserSearchForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(user_name=username)
                my_user = User.objects.get(token=request.session['token'][0])

                # Check if a chat room exists between the users
                chat_room = ChatRoom.objects.filter(
                    (Q(user1=my_user.user_name) & Q(user2=user.user_name)) |
                    (Q(user1=user.user_name) & Q(user2=my_user.user_name))
                ).first()

                # If no chat room exists, create one
                if not chat_room:
                    chat_room = ChatRoom.objects.create(
                        user1=my_user.user_name,
                        user2=user.user_name
                    )

                # Get the last message details
                last_message = Message.objects.filter(room=chat_room).last()
                last_message_text = last_message.text if last_message else ''
                last_message_time = last_message.timestamp.strftime('%H:%M') if last_message else ''

                # Prepare user data
                user_data = {
                    'id': user.id,
                    'name': user.name,
                    'user_name': user.user_name,
                    'email': user.email,
                    'has_chat_room': True,
                    'chat_room_id': chat_room.id
                }

                # Prepare chat room data
                chat_room_data = [{
                    'id': chat_room.id,
                    'user_name': user.user_name,
                    'last_message': last_message_text,
                    'last_message_time': last_message_time
                }]
                return JsonResponse({
                    'success': True,
                    'user': user_data,
                    'chat_rooms': chat_room_data
                })
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'{username} does not exist'})
            except Exception as e:
                logging.error(f'Error in search_user: {e}')
                return JsonResponse({'success': False, 'error': 'An unexpected error occurred'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def get_room_messages(request, room_id):
    if request.method == 'GET':
        cr = get_object_or_404(ChatRoom, id=room_id)
        messages = Message.objects.filter(room=cr).order_by('timestamp')
        message_list = [{'sender': message.sender.user_name, 'content': message.text, 'timestamp': message.timestamp}
                        for message in messages]
        return JsonResponse({'messages': message_list})
