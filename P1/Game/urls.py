from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from . import views
from P1 import settings

urlpatterns = [
    url(r'^$', login_required(views.HomeView.as_view()), name='home'),
    url(r'^game/(?P<game_key>[\w]+)/$', login_required(views.GameView.as_view()), name='game'),
    url(r'^accounts/login/$', views.LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', login_required(views.logout_view), name='logout'),
    url(r'^message/create/$', login_required(views.create_message), name='create_message'),
    url(r'^resource/activate/$', login_required(views.security_resource_activate), name='security_resource_activate'),
    url(r'^resource/complete/$', login_required(views.research_resource_complete), name='research_resource_complete'),
    url(r'^sanction/$', login_required(views.sanction), name='sanction'),
    url(r'^props/$', login_required(views.give_props), name='sanction'),
    url(r'^managersanction/$', login_required(views.manager_sanction), name='manager_sanction'),
    url(r'^tick/complete/$', login_required(views.check_tick_complete), name='check_tick_complete'),
]
