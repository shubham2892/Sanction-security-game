import json

import requests
from django.contrib.auth import logout
from django.contrib.humanize.templatetags.humanize import apnumber
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse, HttpResponseServerError
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from Game.models import Player, Game, Message, PlayerTick, Tick, Sanction, SANCTION, PASS

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


class OnboardingView(TemplateView):
    template_name = "onboarding_1.html"

    def get_context_data(self, **kwargs):
        context = super(OnboardingView, self).get_context_data(**kwargs)

        return context


class GameFlowView(TemplateView):
    template_name = "onboaring_tabular.html"

    def get_context_data(self, **kwargs):
        context = super(GameFlowView, self).get_context_data(**kwargs)

        try:
            game_set = GameSets.objects.get(user=self.request.user)
            demo_game_url = "/game/" + str(game_set.demo_id.game_key)
            game_url_1 = "/game/" + str(game_set.game_id1.game_key)
            game_url_2 = "/game/" + str(game_set.game_id2.game_key)
            ganme_url_3 = "/game/" + str(game_set.game_id3.game_key)

        except ObjectDoesNotExist:
            raise Http404

        context['demo_game_url'] = demo_game_url
        context['game_url_1'] = game_url_1
        context['game_url_2'] = game_url_2
        context['game_url_3'] = ganme_url_3
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

        # Get current total score for bar normalization
        # highscore = Player.objects.all().aggregate(Max('score')).get("score__max")
        # context['highscore'] = highscore

        return context


def create_event_stream(tick):
    attack = tick.attack.get_classification_display
    remaining_rounds = tick.game._ticks - tick.number

    update_url = '/event-attack'
    data = "{}\n{}\n\n".format(attack, remaining_rounds)
    headers = {'content_type': 'text/event-stream', 'Cache-Control': 'no-cache'}
    r = requests.get(update_url, data={'data': data}, headers=headers)


def event_stream_player_score_update(player):
    if player.manager_sanctioned:
        status = 'Manager Sanctioned'
    elif player.peer_sanctioned:
        status = 'Peer Sanctioned'
    else:
        status = 'moved'
    score = player.score
    vulnerabilities = []
    for vulenerability in player.vulnerability.security_resources.all():
        if vulenerability.active:
            vulnerabilities.append(vulenerability.get_classification_display)
    update_url = '/event-score-update'
    data = "{}\n{}\n{}\n".format(status, score, vulnerabilities)
    headers = {'content_type': 'text/event-stream', 'Cache-Control': 'no-cache'}
    r = requests.get(update_url, data={'data': data}, headers=headers)


@csrf_exempt
def create_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('the_message')
        response_data = {}

        game_key = request.POST.get('game_key')
        game = Game.objects.get(game_key=game_key)
        player = game.player_set.get(user=request.user)
        tick = game.current_tick
        message = Message(content=message_text, created_by=player, game=game, tick=tick)
        message.save()

        response_data['result'] = 'Create post successful!'
        response_data['message_pk'] = message.pk
        response_data['content'] = message.content
        response_data['game_key'] = game.game_key
        response_data['created_by'] = message.created_by.user.username

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"What?! This can't be happening?!": "Stop trying to hack the game."}),
            content_type="application/json"
        )




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


@csrf_exempt
def player_peer_sanctioned(request):
    if request.method == 'POST':
        sanctioner = Player.objects.get(pk=request.POST.get("sanctioner_pk"))

        if sanctioner.can_move:
            if sanctioner.manager_sanctioned:
                return HttpResponse(
                    json.dumps({
                        "result": "You have been sanctioned by the manager. You can only click on the 'Pass' button to pass this round."}),
                    content_type="application/json"
                )
            elif sanctioner.sanctioned:
                return HttpResponse(
                    json.dumps({
                        "result": "You have been peer sanctioned. You can only click on the 'Pass' button to pass this round."}),
                    content_type="application/json"
                )
            else:
                # TODO: Add check if sanctionee has been already peer sanctioned or manager sanctioned
                # TODO: Notify other players about status and score update

                player_tick = PlayerTick(player=sanctioner, tick=sanctioner.game.current_tick)
                player_tick.action = SANCTION
                player_tick.save()
                tick = Tick.objects.get(pk=request.POST.get("tick_pk"))
                sanctionee = Player.objects.get(pk=request.POST.get("sanctionee_pk"))
                sanction = Sanction.create(sanctioner, sanctionee, tick)
                response_data = {}
                response_data["sanctioned"] = True
                response_data['result'] = "You have sanctioned Player " + apnumber(sanctionee.number).capitalize()
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"result": "You have already moved this round."}),
                                content_type="application/json")
    else:
        return HttpResponse(json.dumps({"What?! This can't be happening?!": "Stop trying to hack the game."}),
                            content_type="application/json")


@csrf_exempt
def check_tick_complete(request):
    if request.method == 'POST':
        tick = Tick.objects.get(pk=request.POST.get("tick_pk"))
        response_data = {}

        # End the game if it's complete
        if tick.game.ticks < 0:
            tick.game.complete = True
            tick.game.save()

        response_data["game_complete"] = tick.game.complete
        response_data["tick_complete"] = tick.complete

        # if tick.complete:
        #     manager_sanction(tick)

        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({"What?! This can't be happening?!": "Stop trying to hack the game."}),
            content_type="application/json"
        )


@csrf_exempt
def pass_round(request):
    if request.method == 'POST':

        # TODO: Notify other players about status and score update

        player = Player.objects.get(pk=request.POST.get('player_pk'))
        player_tick = PlayerTick(player=player, tick=player.game.current_tick)
        if player.can_move:
            if player.manager_sanctioned:
                response_data = {}

                # fix security tasks if counter is odd; since we fix a security task when clicked twice
                # stats = Statistics(game=player.game, player=player, player_tick=player_tick)
                player.counter = player.counter + 1
                print "Latest sanction number:{}".format(player.sanctionee_by_manager.latest("tick_number").tick_number)
                print "current number:{}".format(player.game.current_tick.number)
                vulnerabilities_fixed = ""
                if player.sanctionee_by_manager.latest("tick_number").tick_number == player.game.current_tick.number:
                    if player.blue_status == False:
                        print "trying to fix blue"
                        response_data["resource"] = "blue"
                        player.blue_status = True

                        for vulnerability in player.vulnerabilities.security_resources.filter(classification=1):
                            vulnerability.active = True
                            vulnerability.save()
                        player.nf_blue += 1
                        player.save()
                        for capability in player.capabilities.security_resources.filter(classification=1):
                            capability.active = True
                            capability.save()

                        # stats.nf_finished_task = player.nf_blue
                        # stats.type_of_task = 5
                        vulnerabilities_fixed += "blue"
                        response_data['result'] = "You've fixed {} vulnerability".format(vulnerabilities_fixed)
                        print "fixed blue vulnerability"
                    if player.red_status == False:
                        response_data["resource"] = "red"
                        player.red_status = True
                        for vulnerability in player.vulnerabilities.security_resources.filter(classification=2):
                            vulnerability.active = True
                            vulnerability.save()

                        player.nf_red += 1
                        player.save()
                        for capability in player.capabilities.security_resources.filter(classification=2):
                            capability.active = True
                            capability.save()

                        # stats.nf_finished_task = player.nf_red
                        # stats.type_of_task = 3
                        vulnerabilities_fixed += " red"
                        response_data['result'] = "You've fixed {} vulnerability".format(vulnerabilities_fixed)
                        print "fixed red vulnerability"
                    if player.yellow_status == False:
                        response_data["resource"] = "yellow"
                        player.yellow_status = True
                        for vulnerability in player.vulnerabilities.security_resources.filter(classification=3):
                            vulnerability.active = True
                            vulnerability.save()

                        player.nf_yellow += 1
                        player.save()

                        for capability in player.capabilities.security_resources.filter(classification=3):
                            capability.active = True
                            capability.save()

                        # stats.nf_finished_task = player.nf_yellow
                        # stats.type_of_task = 4
                        vulnerabilities_fixed += " yellow"
                        response_data['result'] = "You've fixed {} vulnerability".format(vulnerabilities_fixed)
                        print "fixed yellow vulnerability"
                        # stats.save()
                        # print stats
                else:
                    response_data['resource'] = "null"
                    response_data['result'] = "You've clicked pass."

                player_tick.action = PASS
                player_tick.save()

                if player.counter == player.counter_sum:
                    player.counter = 0
                    player.counter_sum = 0
                    player.save()

                return HttpResponse(json.dumps(response_data), content_type="application/json")
            elif player.sanctioned:
                player_tick.action = PASS
                player_tick.save()
                response_data = {}
                response_data['resource'] = "null"
                response_data['result'] = "You've clicked pass."
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                print "Something wrong. You shouldn't see the pass button if you are not sanctioned by the manager."
                return HttpResponse(
                    json.dumps({"result": "What?! You should not see the pass button now."}),
                    content_type="application/json")
        else:
            return HttpResponse(
                json.dumps({"result": "You have already moved this round."}),
                content_type="application/json"
            )

    else:
        return HttpResponse(
            json.dumps({"What?! This can't be happening?!": "Stop trying to hack the game."}),
            content_type="application/json"
        )

# @csrf_exempt
# def event_stream(request):
#     def eventStream():
#         yield "data:Server Sent Data\n\n"
#
#     response = HttpResponse(eventStream(), content_type="text/event-stream")
#     response['Cache-Control'] = 'no-cache'
#     return response
