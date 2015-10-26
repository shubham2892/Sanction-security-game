from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import models

from datetime import timedelta
from random import choice
import random


''' Resource classifications by color '''
BLUE = 1
RED = 2
YELLOW = 3

RESOURCE_CLASSIFICATIONS = (
    (BLUE, "blue"),
    (RED, "red"),
    (YELLOW, "yellow"),
)


''' A Research Resource for completing a Research Task '''
class ResearchResource(models.Model):
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS, null=True, blank=True)
    complete = models.BooleanField(default=False)

    def __unicode__(self):
        if self.complete:
            return u'Completed %s Resource' % (self.get_classification_display().capitalize())
        else:
            return u'Incomplete %s Resource' % (self.get_classification_display().capitalize())

    # If no resource classification is specified before saving, a random classification is selected
    @classmethod
    def create(cls):
        research_resource = cls(classification=random.randint(1,3))
        research_resource.save()
        return research_resource


''' A Research Task comprised of some number of Research Resources '''
class ResearchObjective(models.Model):

    # Research Objective types
    WORKSHOP = 1
    CONFERENCE = 2
    JOURNAL = 3

    RESEARCH_OBJECTIVES = (
        (WORKSHOP,  "workshop"),
        (CONFERENCE, "conference"),
        (JOURNAL, "journal"),
    )

    name = models.IntegerField(choices=RESEARCH_OBJECTIVES, default=None)
    required_resources = models.ManyToManyField(ResearchResource)
    value = models.IntegerField(null=True, blank=True)
    deadline = models.IntegerField(null=True, blank=True)  # deadline not in use yet
    complete = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s Objective' % (self.get_name_display().capitalize())

    # Creates and saves a ResearchObjective object of the provided name parameter
    @classmethod
    def create(cls, name):

        research_objective = cls(name=name, value=name*10)   # Fix value for each objective
        research_objective.save()
        for i in range(name):
            research_resource = ResearchResource.create()
            research_objective.required_resources.add(research_resource)

        research_objective.save()
        return research_objective

    # Returns a set of objects containing one of each Reserarch Objective types
    @classmethod
    def get_set(self):
        research_objective_set = []
        for (x, y) in self.RESEARCH_OBJECTIVES:
            new_objective = self.create(x)
            research_objective_set.append(new_objective)

        return research_objective_set


''' A Security Resource for protecting against an Attack '''
class SecurityResource(models.Model):
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS)
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s Security Resource' % (self.get_classification_display().capitalize())

    @classmethod
    def create(cls, classification):
        security_resource = cls(classification=classification)
        security_resource.save()
        return security_resource


''' A player's set of vulnerabilities or capabilities '''
class SecuritySet(models.Model):

    security_resources = models.ManyToManyField(SecurityResource)

    def __unicode__(self):
        return u'Security Set'

    @classmethod
    def create(cls):
        security_set = cls()
        security_set.save()
        for (x,y) in RESOURCE_CLASSIFICATIONS:
            security_resource = SecurityResource.create(x)
            security_set.security_resources.add(security_resource)

        security_set.save()
        return security_set


''' An Attack Resource for issuing an attack against a Research Resource '''
class AttackResource(models.Model):
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS)

    def __unicode__(self):
        return u'%s Attack Resource' % (self.classification.get_classification_display().capitalize())


''' A Player - How do we make it so that a player may only play once '''
class Player(models.Model):
    user = models.ForeignKey(User)
    score = models.IntegerField(default=0, editable=False)
    number = models.IntegerField(default=0, editable=False)
    research_objectives = models.ManyToManyField(ResearchObjective)
    vulnerabilities = models.OneToOneField(SecuritySet, related_name="vulnerabilities", default=None)
    capabilities = models.OneToOneField(SecuritySet, related_name="capabilities", default=None)


    def __unicode__(self):
        return u'%s %s (%s)' % (self.user.first_name, self.user.last_name, self.user.email)

    @property
    def name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def workshop(self):
        return self.research_objectives.filter(name=ResearchObjective.WORKSHOP, complete=False)

    @property
    def conference(self):
        return self.research_objectives.filter(name=ResearchObjective.CONFERENCE, complete=False)

    @property
    def journal(self):
        return self.research_objectives.filter(name=ResearchObjective.JOURNAL, complete=False)

    @classmethod
    def create(cls, user):
        player = cls(user=user, vulnerabilities=SecuritySet.create(), capabilities=SecuritySet.create())
        player.save()
        for objective in ResearchObjective.get_set():
            player.research_objectives.add(objective)

        player.save()
        return player


''' The Game object for maintaining game state and players '''
class Game(models.Model):

    GAME_KEY_LENGTH = 5

    players = models.ManyToManyField(Player)
    ticks = models.IntegerField()
    game_key = models.CharField(max_length=GAME_KEY_LENGTH, unique=True, null=True, blank=True, editable=False)

    def __unicode__(self):
        return u'%s' % (self.game_key)

    def generate_random_alphanumeric(self, length=GAME_KEY_LENGTH):
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
        players = self.players.all()
        if players.filter(number=0).exists():
            player_number = 1;
            for player in self.players.all():
                player.number = player_number
                player.save()
                player_number+=1


''' Group Message object '''
class Message(models.Model):
    game = models.ForeignKey(Game, null=True)
    created_by = models.ForeignKey(Player, null=True)
    content = models.TextField(max_length=500)

    # Anonymize players in chat
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




