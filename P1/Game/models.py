from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from random import choice
from django.db import IntegrityError
import random

# A Player - How do we make it so that a player may only play once?
class Player(models.Model):
    user = models.ForeignKey(User)
    score = models.IntegerField(default=0)
    number = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s %s (%s)' % (self.user.first_name, self.user.last_name, self.user.email)

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
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS, null=True, blank=True)
    complete = models.BooleanField(default=False)

    def __unicode__(self):
        if self.complete:
            return u'Completed %s Resource' % (self.classification)
        else:
            return u'Incomplete %s Resource' % (self.classification)

    # If no resource classification is specified before saving, a random classification is selected
    def save(self, *args, **kwargs):
        if not self.classification:
            self.classification = random.randint(1,3)


# A Security Resource for protecting against an Attack
class SecurityResource(models.Model):
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS)
    active = models.BooleanField(default=False)

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

    owner = models.ForeignKey(Player)
    name = models.IntegerField(choices=RESEARCH_TASKS, default=None)
    required_resources = models.ManyToManyField(ResearchResource, blank=True)
    value = models.IntegerField(null=True, blank=True)
    deadline = models.IntegerField(null=True, blank=True)
    complete = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s Objective' % (self.name)



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
        # Assign the game a unique game_key
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

        # Assign persistent player numbers for the game
        # need to ensure this happens only once
        player_number = 1;

        for player in self.players.all():
            player.number = player_number
            player.save()
            player_number+=1



class Message(models.Model):
    game = models.ForeignKey(Game, null=True)
    created_by = models.ForeignKey(Player, null=True)
    content = models.TextField(max_length=500)

    # Used for anonymizing players in chat
    @property
    def anonymize(self):
        player_list = [player for player in self.game.players.all()]
        created_by = player_list.index(self.created_by) + 1
        return created_by

    def __unicode__(self):
        content = (self.content[:75] + '...') if len(self.content) > 25 else self.content
        if self.game and self.created_by:
            return u'Game #%s: %s said, \"%s\"' % (self.game.game_key,
                                                                        self.created_by.user.username,
                                                                        content)
        else:
            return u'%s' % content




