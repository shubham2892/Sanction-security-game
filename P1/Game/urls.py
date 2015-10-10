from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from P1 import settings
from . import views

urlpatterns = [
    url(r'^$', login_required(TemplateView.as_view(template_name='home.html')), name='home'),
    url(r'^game/(?P<game_key>[\w]+)/$', views.GameView.as_view(), name='game'),
    url(r'^accounts/login/$', views.LoginOrRegisterView.as_view(), name='login'),
    url(r'^accounts/logout/$', TemplateView.as_view(template_name='home.html'), name='logout'),
]
