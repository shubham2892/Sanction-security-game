from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import CreateView

from models import Player, Game, Message
from forms import RegistrationForm, CreateMessageForm



class HomeView(TemplateView):
    template_name = "home.html"

    def games(self):
        return Game.objects.all()



class MultipleFormView(FormView):
    form_class = None
    form_name = None

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(forms=self.get_forms()))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(forms=self.get_forms()))

    def form_valid(self, form):
        return getattr(self, "%s_form_valid" % self.form_name)(form)

    def get_forms(self):
        forms = {}
        for form_name, form_class in self.get_form_classes().items():
            forms[form_name] = self.get_form(form_class)
        return forms

    def get_form_classes(self):
        return self.form_classes

    def get_form_class(self):
        if self.request.method in ('POST', 'PUT'):
            if not self.form_class:
                for form_name, form_class in self.get_form_classes().items():
                    if form_name in self.request.POST:
                        self.form_class = form_class
                        self.form_name = form_name
                        break
                if not self.form_class:
                    raise Exception("Button name does not match any items in form_classes.")
            return self.form_class

    def get_form(self, form_class):
        if form_class == self.get_form_class():
            return form_class(**self.get_form_kwargs())
        else:
            return form_class()



class LoginOrRegisterView(MultipleFormView):
    template_name = 'accounts/login.html'
    form_classes = {
        'login': AuthenticationForm,
        'registration': RegistrationForm,
    }

    def login_form_valid(self, form):
        login(self.request, self.authenticate_user(form))
        return HttpResponseRedirect(self.get_success_url())

    def registration_form_valid(self, form):
        form.save()
        # Login the new User
        login(self.request, self.authenticate_user(form))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.request.GET.get("next", reverse('home'))

    def authenticate_user(self, form):
        username = form.cleaned_data['username']
        try:
            password = form.cleaned_data['password']
        except KeyError:
            password = form.cleaned_data['password1']

        return authenticate(username=username, password=password)


class GameView(TemplateView):

    template_name = "game.html"

    # Overwritten "POST" method
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()

        # Create a new message
        message = context["message"]
        if message.is_valid():
            m = message.save()
            m.created_by = Player.objects.get(user=request.user)
            m.game = Game.objects.get(game_key=self.kwargs['game_key'])
            m.save()
            return HttpResponseRedirect('')

        return super(TemplateView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(GameView, self).get_context_data(**kwargs)

        # Create message form for group messaging
        message = CreateMessageForm(self.request.POST or None)  # instance= None
        context["message"] = message

        # Get game object that matches URL, else 404
        try:
            game = Game.objects.get(game_key=self.kwargs['game_key'])
        except ObjectDoesNotExist:
            raise Http404
        context["game"] = game

        # Get current player from player view
        me = Player.objects.get(user=self.request.user)
        context["me"] = me

        return context

    def threats(self):

        threats = {"yellow": 20,
                        "red": 40,
                        "blue": 40
                        }

        return threats








