import json

from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse, HttpResponseServerError
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from Game.models import Player, Game, GameSet

''' The user's homepage which displays user game information '''


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context["my_players"] = Player.objects.filter(user=self.request.user)

        return context


''' The login form view '''


def logout_view(request):
    logout(request)
    return redirect('login')


class MonitorView(TemplateView):
    template_name = "monitor.html"

    def get_context_data(self, **kwargs):
        context = super(MonitorView, self).get_context_data(**kwargs)

        try:

            players = Player.objects.filter(game__game_key=self.kwargs['game_key'])
        except:
            raise Http404
        context['players'] = players
        return context


class GameFlowView(TemplateView):
    template_name = "onboarding_tabular.html"

    def get_context_data(self, **kwargs):
        context = super(GameFlowView, self).get_context_data(**kwargs)

        try:
            game_set = GameSet.objects.get(user=self.request.user)
            demo_game_url_1 = "/game/" + str(game_set.demo_game_1.game_key)
            demo_game_url_2 = "/game/" + str(game_set.demo_game_2.game_key)
            game_url_1 = "/game/" + str(game_set.game_1.game_key)
            game_url_2 = "/game/" + str(game_set.game_2.game_key)
            game_url_3 = "/game/" + str(game_set.game_3.game_key)
            game_url_4 = "/game/" + str(game_set.game_4.game_key)

        except ObjectDoesNotExist:
            raise Http404

        context['demo_game_url_1'] = demo_game_url_1
        context['demo_game_url_2'] = demo_game_url_2
        context['game_url_1'] = game_url_1
        context['game_url_2'] = game_url_2
        context['game_url_3'] = game_url_3
        context['game_url_4'] = game_url_4
        context['game_key_1'] = game_set.game_1.game_key
        context['game_key_2'] = game_set.game_2.game_key
        context['game_key_3'] = game_set.game_3.game_key
        context['game_key_4'] = game_set.game_4.game_key
        context['game_chat_link'] = game_set.chat_link

        return context


class GameView(TemplateView):
    template_name = "game.html"

    def get_context_data(self, **kwargs):
        context = super(GameView, self).get_context_data(**kwargs)

        # Get game object that matches URL, else 404
        try:
            game = Game.objects.get(game_key=self.kwargs['game_key'])
        except ObjectDoesNotExist:
            raise Http404
        context["game"] = game

        # Get current player from player view
        try:
            me = Player.objects.get(user=self.request.user, game=game)
        except ObjectDoesNotExist:
            raise Http404
        context["me"] = me

        # Player list with "me" as the first object
        players = [me] + [player for player in Player.objects.filter(game=game).exclude(user=me.user)]
        context["players"] = players

        return context


@csrf_exempt
def remove_player(request):
    if request.method == 'POST':
        try:
            if request.user.is_superuser:
                # TODO Change this hard coding to the dummy game
                game = Game.objects.get(id='30')
                Player.objects.filter(id=request.POST.get("player_id")).update(game=game)
            else:
                return HttpResponse(
                    json.dumps({
                        "result": False}),
                    content_type="application/json"
                )
        except:
            return HttpResponseServerError

        return HttpResponse(
            json.dumps({
                "result": True}),
            content_type="application/json"
        )
