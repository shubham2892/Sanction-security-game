from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta


# A Player
class Player(models.Model):
    user = models.OneToOneField(User)

    @property
    def name(self):
        return self.user.get_username()

    @property
    def is_admin(self):
        return self.is_superuser()


# A Resource Classification used to match Security, Attack, and Research resources
class ResourceClassification(models.Model):
    classification = models.IntegerField()

    @property
    def name(self):
        return self.classification()


# A Research Resource for completing a Research Task
class ResearchResource(models.Model):
    name =  models.CharField(max_length = 25)
    description = models.CharField(max_length = 150)
    classification = models.ForeignKey(ResourceClassification)

    @property
    def name(self):
        return self.name()


# A Security Resource for protecting against an Attack
class SecurityResource(models.Model):
    name =  models.CharField(max_length = 25)
    description = models.CharField(max_length = 150)
    classification = models.ForeignKey(ResourceClassification)

    @property
    def name(self):
        return self.name()


# An Attack Resource for issuing an attack against a Research Resource
class AttackResource(models.Model):
    name =  models.CharField(max_length = 25)
    description = models.CharField(max_length = 150)
    classification = models.ForeignKey(ResourceClassification)

    @property
    def name(self):
        return self.name()


# A Research Task comprised of some number of Research Resources
class ResearchTask(models.Model):
    name = models.CharField(max_length=25)
    required_resources = models.ManyToManyField(ResearchResource)
    value = models.IntegerField()
    deadline = models.IntegerField()

    @property
    def name(self):
        return self.name()


# A Deck of Attack Resources
class AttackDeck(models.Model):
    attack_resources = models.ManyToManyField(AttackResource)


class Game(models.Model):
    players = models.ManyToManyField(Player)
    deck = models.ForeignKey(AttackDeck)
    rounds = models.IntegerField()
    duration = models.DurationField(default=timedelta(hours=1))
    game_key = models.CharField(max_length=15)

    @property
    def name(self):
        return self.game_key()



