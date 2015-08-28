from django.contrib import admin
from Game.models import *

# Register your models here.
admin.site.register(Player)
admin.site.register(ResourceClassification)
admin.site.register(ResearchResource)
admin.site.register(ResearchTask)
admin.site.register(AttackResource)
admin.site.register(SecurityResource)
admin.site.register(AttackDeck)
admin.site.register(Game)

