from django.contrib import admin
from Game.models import *

# Register your models here.
admin.site.register(Player)
admin.site.register(Game)
admin.site.register(Message)
admin.site.register(Tick)
admin.site.register(AttackResource)
