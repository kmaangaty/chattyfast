import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from .forms import UserSearchForm
from .models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ChatRoom, Message
from django.shortcuts import render, redirect
from .models import User


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
    """
    Handles user login and registration.

    If the request method is POST, this view will:
    - Attempt to log the user in if 'method' is 'log'.
    - Attempt to register a new user if 'method' is 'reg'.

    On successful login:
    - Sets a session token and updates the user's token in the database.
    - Redirects to the home page.

    On successful registration:
    - Creates a new user with a unique token.
    - Redirects to the home page.

    On failure:
    - Renders the login page with an appropriate error message.

    Args:
        request (HttpRequest): The request object containing user input.

    Returns:
        HttpResponse: The response object that either redirects or renders a page.
    """
    if request.method == 'POST':
        # Retrieve user inputs
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        method = request.POST.get('method')

        # Check if the user exists in the database
        try:
            user_data = User.objects.get(user_name=user_name)
            user_exist = True
        except User.DoesNotExist:
            user_exist = False

        # Generate a new token
        token = create_token()

        if method == 'log':
            # Attempt to log in the user
            if user_exist and password == user_data.password:
                # Successful login: Set session token and update user token
                request.session['token'] = [token]
                user_data.token = token
                user_data.save()
                return redirect('/')
            else:
                # Invalid login credentials: Render login page with error
                return render(request, 'login.html', {'error': 'Invalid login credentials'})

        elif method == 'reg':
            # Attempt to register a new user
            if not user_exist:
                email = request.POST.get('email')
                # Create new user with generated token
                request.session['token'] = [create_token()]
                User.objects.create(
                    UID=create_token(),
                    user_name=user_name,
                    password=password,
                    email=email,
                    token=token
                )
                return redirect('/')
            else:
                # User already exists: Render login page with error
                return render(request, 'login.html', {'error': 'User already exists'})

    # If request method is not POST, render the login page
    return render(request, 'login.html')


def create_token():
    import string
    import secrets
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(32))
    return token


@login_required
def home(request):
    """
    Renders the home page for logged-in users.

    This view is protected by the `login_required` decorator,
    which ensures that only authenticated users can access this page.

    Args:
        request (HttpRequest): The request object containing user information.

    Returns:
        HttpResponse: The response object that renders the 'home.html' template.
    """
    return render(request, 'home.html')


def get_user_chat_rooms(request):
    """
    Retrieves and returns a list of chat rooms for the currently authenticated user.

    This view fetches the chat rooms where the current user is either user1 or user2.
    It also retrieves the most recent message for each chat room.

    Args:
        request (HttpRequest): The request object containing user session information.

    Returns:
        JsonResponse: A JSON response containing the list of chat rooms with their details.
    """
    # Retrieve the user from the database based on the session token
    user = User.objects.get(token=request.session['token'][0])

    # Query to find chat rooms where the user is either user1 or user2
    chat_rooms = ChatRoom.objects.filter(
        Q(user1=user.user_name) | Q(user2=user.user_name)
    ).prefetch_related('message_set').distinct()

    chat_room_data = []
    for room in chat_rooms:
        # Retrieve the last message in the chat room
        last_message = room.message_set.last()

        # Prepare chat room data including last message details
        chat_room_data.append({
            'id': room.id,
            'user_name': room.user2 if room.user1 == user.user_name else room.user1,
            'last_message': last_message.text if last_message else '',
            'last_message_time': last_message.timestamp.strftime('%H:%M') if last_message else ''
        })

    # Return the chat room data as a JSON response
    return JsonResponse({'chat_rooms': chat_room_data})


def get_or_create_room(user1, user2):
    """
    Retrieves an existing chat room between two users or creates a new one if it does not exist.

    This function ensures that the provided user instances are valid and have proper IDs.
    It uses the `get_or_create` method to either fetch an existing chat room or create a new one.

    Args:
        user1 (User): The first user in the chat room.
        user2 (User): The second user in the chat room.

    Returns:
        ChatRoom: The chat room instance between the two users.

    Raises:
        TypeError: If either `user1` or `user2` is not an instance of `User`.
        ValueError: If either `user1` or `user2` has an invalid ID.
    """
    if not (isinstance(user1, User) and isinstance(user2, User)):
        raise TypeError("Expected instances of User")

    # Ensure users have valid IDs
    if user1.id is None or user2.id is None:
        raise ValueError("One or both users have invalid IDs")

    # Ensure user1 is always less than or equal to user2 by ID for consistent room creation
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
