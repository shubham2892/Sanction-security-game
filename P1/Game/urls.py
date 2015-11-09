from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from . import views
from P1 import settings

urlpatterns = [
    url(r'^$', login_required(views.HomeView.as_view()), name='home'),
    url(r'^game/(?P<game_key>[\w]+)/$', views.GameView.as_view(), name='game'),
    url(r'^accounts/login/$', views.LoginOrRegisterView.as_view(), name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),
    url(r'^message/create/$', views.create_message, name='create_message'),
    url(r'^resource/activate/$', views.security_resource_activate, name='security_resource_activate'),
    url(r'^resource/complete/$', views.research_resource_complete, name='research_resource_complete'),
    url(r'^sanction/$', views.sanction, name='sanction'),
]
