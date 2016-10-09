from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    # Game App URLs
    url(r'^', include("Game.urls")),
    # Django Admin Pages
    url(r'^admin/', include(admin.site.urls)),
]
