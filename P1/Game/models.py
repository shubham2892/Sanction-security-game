from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from random import choice
from django.db import IntegrityError
import random


# A Player
class Player(models.Model):
    first_name = models.CharField(max_length=50, default=None)
    last_name = models.CharField(max_length=50, default=None)
    email = models.CharField(max_length=50, default=None, unique=True)


    def __unicode__(self):
        return u'%s %s (%s)' % (self.first_name, self.last_name, self.email)

    @property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name)



# Resource classifications by color
RESOURCE_CLASSIFICATIONS = (
    (1, "BLUE"),
    (2, "RED"),
    (3, "YELLOW"),
)

# A Research Resource for completing a Research Task
class ResearchResource(models.Model):
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS)

    def __unicode__(self):
        return u'%s Research Resource' % (self.classification)


# A Security Resource for protecting against an Attack
class SecurityResource(models.Model):
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS)

    def __unicode__(self):
        return u'%s Security Resource' % (self.classification)


# An Attack Resource for issuing an attack against a Research Resource
class AttackResource(models.Model):
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS)

    def __unicode__(self):
        return u'%s Attack Resource' % (self.classification)


# A Research Task comprised of some number of Research Resources
class ResearchObjective(models.Model):

    RESEARCH_TASKS = (
        (1, "Workshop"),
        (2, "Conference"),
        (3, "Journal"),
    )

    name = models.IntegerField(choices=RESEARCH_TASKS, default=None)
    required_resources = models.ManyToManyField(ResearchResource)
    value = models.IntegerField(null=True, blank=True)
    deadline = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return u'%s Objective' % (self.name)

    def save(self, *args, **kwargs):
        pass


class Game(models.Model):
    game_key_length = 5

    players = models.ManyToManyField(Player)
    ticks = models.IntegerField()
    game_key = models.CharField(max_length=game_key_length, unique=True, null=True, blank=True, editable=False)

    def __unicode__(self):
        return u'%s' % (self.game_key)

    def generate_random_alphanumeric(self, length=game_key_length):
        return ''.join(random.choice('0123456789ABCDEF') for i in range(length))

    def save(self, *args, **kwargs):
        if not self.game_key:
            self.game_key = self.generate_random_alphanumeric()
            # using your function as above or anything else
        success = False
        failures = 0
        while not success:
            try:
                super(Game, self).save(*args, **kwargs)
            except IntegrityError:
                 failures += 1
                 if failures > 5: # or some other arbitrary cutoff point at which things are clearly wrong
                     raise
                 else:
                     # looks like a collision, try another random value
                     self.game_key = self.generate_random_alphanumeric()
            else:
                 success = True






