from django.contrib import admin
from Game.models import *

# Register your models here.
admin.site.register(Player)
admin.site.register(ResearchResource)
admin.site.register(ResearchObjective)
admin.site.register(SecurityResource)
admin.site.register(AttackResource)
admin.site.register(Game)

