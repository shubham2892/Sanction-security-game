from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

from . import views

urlpatterns = [
    url(r'^$', login_required(views.HomeView.as_view()), name='home'),
    url(r'^game/(?P<game_key>[\w]+)/$', login_required(views.GameView.as_view()), name='game'),
    url(r'^accounts/login/$', LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', login_required(views.logout_view), name='logout'),
    url(r'^monitor/(?P<game_key>[\w]+)/$', login_required(views.MonitorView.as_view()), name='monitor'),
    url(r'^player/remove/$', login_required(views.remove_player), name='remove_player'),
    url(r'^onboarding/$', login_required(views.GameFlowView.as_view()), name='onboarding'),
]
