import debug_toolbar
from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

from . import views

urlpatterns = [
    url(r'^$', login_required(views.HomeView.as_view()), name='home'),
    url(r'^game/(?P<game_key>[\w]+)/$', login_required(views.GameView.as_view()), name='game'),
    url(r'^accounts/login/$', LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', login_required(views.logout_view), name='logout'),
    url(r'^message/create/$', login_required(views.create_message), name='create_message'),
    url(r'^resource/activate/$', login_required(views.security_resource_activate), name='security_resource_activate'),
    url(r'^resource/complete/$', login_required(views.research_resource_complete), name='research_resource_complete'),
    url(r'^player/sanction/$', login_required(views.player_peer_sanctioned), name='peer_sanction'),
    # url(r'^sanction/$', login_required(views.sanction), name='sanction'),
    url(r'^tick/complete/$', login_required(views.check_tick_complete), name='check_tick_complete'),
    url(r'^passround/$', login_required(views.pass_round), name='passround'),
    # url(r'^event-stream/$', MySseEvents.as_view(), name="event-stream"),
    url(r'^monitor/(?P<game_key>[\w]+)/$', login_required(views.MonitorView.as_view()), name='monitor'),
    url(r'^player/remove/$', login_required(views.remove_player), name='remove_player'),
    url(r'^onboarding/$', login_required(views.GameFlowView.as_view()), name='onboarding'),
    url(r'^__debug__/', include(debug_toolbar.urls)),
]
