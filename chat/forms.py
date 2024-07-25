# forms.py

from django import forms
from .models import User, Message


class UserSearchForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label='Username')


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
