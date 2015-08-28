from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from P1 import settings
from Game import views

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='test.html'), name='home'),
    url(r'^game', TemplateView.as_view(template_name="game.html"), name='game'),
    url(r'^login', TemplateView.as_view(template_name="login.html"), name='login'),
]
