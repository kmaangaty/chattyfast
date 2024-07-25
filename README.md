# ChattyFast

## Description
ChattyFast is a real-time chat application built with Django, Django Channels, and WebSockets. It supports one-to-one chat rooms with real-time messaging. The application allows users to search for other users, start chat rooms, and exchange messages instantly.

## Features
- Real-time messaging with WebSockets.
- One-to-one chat rooms.
- User search functionality.
- Dynamic chat room list.
- Message timestamps.

## Installation

### Prerequisites
- Python 3.11.4
- Django 4.x
- Django Channels 4.x
- Redis (for channel layer)

### Steps

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/chattyfast.git
   cd chattyfast
Create a virtual environment and activate it:

sh
Copy code
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install dependencies:

sh
Copy code
pip install -r requirements.txt
Set up Redis:
Follow the instructions on the Redis website to install Redis.

Apply migrations:

sh
Copy code
python manage.py migrate
Create a superuser:

sh
Copy code
python manage.py createsuperuser
Run the development server:

sh
Copy code
python manage.py runserver
Start the WebSocket server:
Ensure Redis server is running and start the Django Channels layer:

sh
Copy code
daphne -b 0.0.0.0 -p 8001 chattyfast.asgi:application
Usage
Register or log in to the application.
Search for users by username.
Start a chat room and send messages in real-time.
View chat history with timestamps.
Project Structure
arduino
Copy code
chattyfast/
├── chat/
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── chat/
│           └── index.html
├── static/
│   └── css/
│   └── js/
├── chattyfast/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── manage.py
└── requirements.txt
API Endpoints
Search User:

URL: /search_user/
Method: POST
Data: {"username": "target_username"}
Response: {"success": True, "user": {...}, "chat_rooms": [...]}
WebSocket Endpoint:

URL: ws://yourdomain/ws/chat/<room_name>/
Contributing
We welcome contributions! Please follow these steps:

Fork the repository.
Create a new branch for your feature:
sh
Copy code
git checkout -b feature/your-feature-name
Make your changes and commit them:
sh
Copy code
git add .
git commit -m "Add your descriptive commit message"
Push your branch to the remote repository:
sh
Copy code
git push origin feature/your-feature-name
Create a pull request to merge your feature branch into the main branch.
License
This project is licensed under the MIT License. See the LICENSE file for details.

perl
Copy code

## Acknowledgments
- Thanks to the Django and Django Channels communities for their awesome documentation and support.

