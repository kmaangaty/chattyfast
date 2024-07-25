# utils.py
from .models import User


def get_user_from_session(request):
    token = request.session.get('token')
    if token:
        try:
            user = User.objects.get(token=token)
            return user
        except User.DoesNotExist:
            return None
    return None
