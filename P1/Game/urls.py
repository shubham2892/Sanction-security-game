from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from P1 import settings
from views import GameView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='login.html'), name='home'),
    url(r'^game/(?P<game_key>[\w]+)/$', GameView.as_view(), name='game'),
    # url(r'^login', TemplateView.as_view(template_name="login.html"), name='login'),
]
