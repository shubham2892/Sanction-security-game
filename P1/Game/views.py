from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.humanize.templatetags.humanize import  apnumber
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import CreateView

from random import random
from itertools import chain
from forms import CreateMessageForm
from models import *
import json


class HomeView(TemplateView):
    template_name = "home.html"

    def games(self):

        user_players = Player.objects.filter(user=self.request.user)
        games = []
        for player in user_players:
            games.append(Game.objects.filter(player=player).first())  #filter().first() won't cause 500 if query doesn't exist

        return games


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


def logout_view(request):
    logout(request)
    return redirect('login')


class GameView(TemplateView):

    template_name = "game.html"

    def get_context_data(self, **kwargs):
        context = super(GameView, self).get_context_data(**kwargs)

        # Add message form to context
        context["message"] = CreateMessageForm()

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


@csrf_exempt
def create_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('the_message')
        response_data = {}

        game_key = request.POST.get('game_key')
        game = Game.objects.get(game_key=game_key)
        player = game.player_set.get(user=request.user)
        message = Message(content=message_text, created_by=player, game=game)
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
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


@csrf_exempt
def security_resource_activate(request):
        if request.method == 'POST':
            player = Player.objects.get(pk=request.POST.get('player_pk'))
            if player.can_move:
                pk = request.POST.get('pk')
                response_data = {}

                security_resource = SecurityResource.objects.get(pk=pk)
                security_resource.active=True
                security_resource.save()

                # After security resource is activated, reactivate capability if necessary
                c = Capabilities.objects.get(player=player).security_resources.get(classification=security_resource.classification)
                c.active = True;
                c.save()

                # End players move
                PlayerTick(player=player, tick=player.game.current_tick).save()

                response_data['result'] = str(security_resource) + ' Activated!  ' + str(security_resource.get_classification_display().capitalize()) + ' capability restored.'

                response_data['pk'] = security_resource.pk
                response_data['active'] = security_resource.active

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            elif player.sanctioned:
                return HttpResponse(
                    json.dumps({"result": "You have been sanctioned. You may not move this round."}),
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
def research_resource_complete(request):
        if request.method == 'POST':
            player = Player.objects.get(pk=request.POST.get('player_pk'))
            if player.can_move:
                pk = request.POST.get('pk')
                response_data = {}

                research_resource = ResearchResource.objects.get(pk=pk)
                capable = player.capabilities.security_resources.get(classification = research_resource.classification)
                if capable.active:
                    research_resource.complete=True
                    research_resource.save()
                else:
                    return HttpResponse(
                    json.dumps({"result": "You are not capable of completing this task. Make sure you patch your vulnerabilities."}),
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
                    player = objective.player
                    player.score += objective.value
                    player.save()
                    objective.save()
                    response_data['result'] = str(objective) + " Completed!"

                # End players move
                PlayerTick(player=player, tick=player.game.current_tick).save()

                response_data['pk'] = research_resource.pk
                response_data['resource_complete'] = research_resource.complete
                response_data['objective_complete'] = objective_completed

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            elif player.sanctioned:
                return HttpResponse(
                    json.dumps({"result": "You have been sanctioned. You may not move this round."}),
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
def sanction(request):
    if request.method == 'POST':
            sanctioner = Player.objects.get(pk=request.POST.get("sanctioner_pk"))
            if sanctioner.can_move:
                sanctionee = Player.objects.get(pk=request.POST.get("sanctionee_pk"))
                tick = Tick.objects.get(pk=request.POST.get("tick_pk"))
                response_data = {}

                # Perform Sanction
                sanction = Sanction.create(sanctioner, sanctionee, tick)

                # End players move
                PlayerTick(player=sanctioner, tick=sanctioner.game.current_tick).save()

                response_date["sanctioned"] = True
                response_data['result'] = "You have sanctioned Player " + apnumber(sanctionee.number).capitalize()

                return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
                )
            elif sanctioner.sanctioned:
                return HttpResponse(
                    json.dumps({"result": "You have been sanctioned. You may not move this round."}),
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
            tick.game.complete =  True
            tick.game.save()

        response_data["game_complete"] = tick.game.complete
        response_data["tick_complete"] = tick.complete

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    else:
        return HttpResponse(
            json.dumps({"What?! This can't be happening?!": "Stop trying to hack the game."}),
            content_type="application/json"
        )



