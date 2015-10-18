from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
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

            # Create Player object from User object
            player = Player()
            player.user = user
            player.save()

        return user


class CreateMessageForm(ModelForm):

    content = forms.CharField(required=True, label='')

    class Meta:
      model = Message
      fields = ("content",)

      def save(self, commit=True):

        # Create User object from cleaned data
        message = super(CreateMessageForm, self).save(commit=False)
        message.content = self.cleaned_data["content"]

        if commit:
            message.save()


        return message

