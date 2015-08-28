from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse

# Create your views here.


from django.contrib.auth import authenticate, login

def home(request):

    if request.user and request.user.is_authenticated:
        pass
    else:
        pass


