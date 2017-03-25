import json

import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.humanize.templatetags.humanize import apnumber
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView

from Game.models import Player, Game, Message, PlayerTick, SecurityResource, Tick, Sanction, SANCTION, SECURITY, \
    Capabilities, Statistics, ResearchResource, RESEARCH_TASK, PASS, RESEARCH_OBJ

''' The user's homepage which displays user game information '''


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context["my_players"] = Player.objects.filter(user=self.request.user)

        return context


''' A form mixin for supporting multiple forms in a single generic view '''


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


''' The login form view '''


class LoginView(MultipleFormView):
    template_name = 'accounts/login.html'
    form_classes = {
        'login': AuthenticationForm,
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


''' A lazy logout view, redirects to login '''


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
        highscore = Player.objects.all().aggregate(Max('score')).get("score__max")
        context['highscore'] = highscore

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
def security_resource_activate(request):
    if request.method == 'POST':
        player = Player.objects.get(pk=request.POST.get('player_pk'))
        player_tick = PlayerTick(player=player, tick=player.game.current_tick)
        if player.can_move:
            if player.manager_sanctioned:
                return HttpResponse(
                    json.dumps({
                        "result": "You have been sanctioned by the manager. You can only click on the 'Pass' button to pass this round."}),
                    content_type="application/json"
                )
            if player.sanctioned:
                return HttpResponse(
                    json.dumps({
                        "result": "You have been peer sanctioned. You can only click on the 'Pass' button to pass this round."}),
                    content_type="application/json"
                )
            else:
                pk = request.POST.get('pk')
                response_data = {}

                security_resource = SecurityResource.objects.get(pk=pk)
                security_resource.active = True
                security_resource.save()

                # update the number of finished security tasks; note the number corresponding to the one in the model
                if security_resource.classification == 1:
                    player.nf_blue += 1
                elif security_resource.classification == 2:
                    player.nf_red += 1
                else:  # for yellow, classification = 3; there is no need to consider "lab" resource_classifications
                    player.nf_yellow += 1

                player.save()

                # print "the resource is "
                # print security_resource.classification
                # Record players action as "Security"
                player_tick.action = SECURITY

                # After security resource is activated, reactivate capability if necessary
                c = Capabilities.objects.get(player=player).security_resources.get(
                    classification=security_resource.classification)
                c.active = True
                c.save()

                # End players move
                print "Saving ticket 3"
                player_tick.save()

                # update Statistics table data; note the number corresponding to the one in the model
                stats = Statistics(game=player.game, player=player, player_tick=player_tick)
                if security_resource.classification == 1:  # blue
                    stats.nf_finished_task = player.nf_blue
                    stats.type_of_task = 5
                elif security_resource.classification == 2:  # red
                    stats.nf_finished_task = player.nf_red
                    stats.type_of_task = 3
                else:  # for yellow, classification = 3
                    stats.nf_finished_task = player.nf_yellow
                    stats.type_of_task = 4
                # print stats
                stats.save()

                response_data['result'] = str(security_resource) + ' Activated!  ' + str(
                    security_resource.get_classification_display().capitalize()) + ' capability restored.'

                response_data['pk'] = security_resource.pk
                response_data['active'] = security_resource.active

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )

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
def research_resource_complete(request):
    if request.method == 'POST':
        player = Player.objects.get(pk=request.POST.get('player_pk'))
        player_tick = PlayerTick(player=player, tick=player.game.current_tick)
        if player.can_move:
            if player.manager_sanctioned:
                return HttpResponse(
                    json.dumps({
                        "result": "You have been sanctioned by the manager. You can only click on the 'Pass' button to pass this round."}),
                    content_type="application/json"
                )
            elif player.sanctioned:
                return HttpResponse(
                    json.dumps({
                        "result": "You have been peer sanctioned. You can only click on the 'Pass' button to pass this round."}),
                    content_type="application/json"
                )
            else:
                pk = request.POST.get('pk')
                response_data = {}

                research_resource = ResearchResource.objects.get(pk=pk)
                capable = player.capabilities.security_resources.get(classification=research_resource.classification)
                if capable.active:
                    research_resource.complete = True
                    research_resource.save()

                    # Record Player's action as "Research Task"
                    player_tick.action = RESEARCH_TASK

                else:
                    return HttpResponse(
                        json.dumps({
                            "result": "You are not capable of completing this task. Make sure you patch your vulnerabilities."}),
                        content_type="application/json"
                    )

                objective_completed = True
                objective = research_resource.researchobjective_set.all().first()
                for resource in objective.research_resources.all():
                    if resource.complete == False:
                        objective_completed = False

                response_data['result'] = str(research_resource) + ' Completed!'

                if objective_completed:
                    objective.complete = True

                    # Record Player's action as "Research Objective"
                    player_tick.action = RESEARCH_OBJ

                    player = objective.player
                    player.score += objective.value
                    # update number of finished research tasks; note the number corresponding to the one in the model
                    if objective.name == 1:
                        player.nf_workshop += 1
                    elif objective.name == 2:
                        player.nf_conference += 1
                    else:
                        player.nf_journal += 1
                    player.save()
                    objective.save()
                    response_data['result'] = str(objective) + " Completed!"
                # End players move
                print "Saving ticket 5"
                player_tick.save()

                if objective_completed:
                    # update Statistics table data; note the number corresponding to the one in the model
                    stats = Statistics(game=player.game, player=player, player_tick=player_tick)
                    if objective.name == 1:  # workshop
                        stats.nf_finished_task = player.nf_workshop
                        stats.type_of_task = 0
                    elif objective.name == 2:  # conference
                        stats.nf_finished_task = player.nf_conference
                        stats.type_of_task = 1
                    else:  # ==3: journal
                        stats.nf_finished_task = player.nf_journal
                        stats.type_of_task = 2
                    # print stats
                    stats.save()

                response_data['pk'] = research_resource.pk
                response_data['resource_complete'] = research_resource.complete
                response_data['objective_complete'] = objective_completed

                # TODO Notify other players about updated score and status

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
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
