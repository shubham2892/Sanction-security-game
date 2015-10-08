from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView
from django.http import Http404
from models import Player, Game
from django.contrib.auth import authenticate, login

def home(request):

    if request.user and request.user.is_authenticated:
        pass
    else:
        pass


class GameView(TemplateView):
    template_name = "game.html"

    def get_context_data(self, **kwargs):

        context = super(GameView, self).get_context_data(**kwargs)
        # player = Player.objects.get(user=self.request.user)

        try:
            game = Game.objects.get(game_key=kwargs['game_key'])
        except ObjectDoesNotExist:
            raise Http404

        context['game'] = game
        return context

