from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
from models import Player, Message

class RegistrationForm(UserCreationForm):
    username = forms.EmailField(required=True, help_text='Your email address')
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):

        # Create User object from cleaned data
        user = super(RegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["username"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user


class CreateMessageForm(forms.ModelForm):
    content = forms.CharField(max_length=500, label='')

    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.TextInput(
                attrs={ 'id': 'message-content', 'required': True, 'placeholder': 'Send a message...' },
            ),
        }


