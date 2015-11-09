from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import models
from django.db.models.signals import post_save

from datetime import timedelta
from random import choice
import random


''' The Game object for maintaining game state and players '''
class Game(models.Model):

    GAME_KEY_LENGTH = 5

    _ticks = models.IntegerField()
    game_key = models.CharField(max_length=GAME_KEY_LENGTH*2, unique=True, null=True, blank=True, editable=False)

    def __unicode__(self):
        return u'Game #%s' % (self.game_key)

    @property
    def ticks(self):
        return self._ticks - self.tick_set.latest('number').number

    @property
    def current_tick(self):
        return self.tick_set.latest('number')

    @property
    def attack(self):
        if self.tick_set.last().attack:
            return self.tick_set.last().attack.get_classification_display()
        else:
            return None

    @property
    def players(self):
        return self.player_set.all()


    def generate_random_alphanumeric(self, length=GAME_KEY_LENGTH):
        return str(Game.objects.count() + 1) + ''.join(random.choice('0123456789ABCDEF') for i in range(length))

    def save(self, *args, **kwargs):

        # Assign the game a unique game_key upon save, if none exists
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

        # Create the first game tick
        if not self.tick_set.all():
            Tick.create(game=self)


''' A Player - How do we make it so that a player may only play once '''
class Player(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    score = models.IntegerField(default=0, editable=False)
    number = models.IntegerField(default=0, editable=False)

    def __unicode__(self):
        return u'%s %s (%s)' % (self.user.first_name, self.user.last_name, self.user.email)

    @property
    def name(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    @property
    def workshop(self):
        objective = self.researchobjective_set.filter(name=ResearchObjective.WORKSHOP, complete=False).first()
        if not objective:
            objective = ResearchObjective.create(ResearchObjective.WORKSHOP, self)
            objective.save()
            self.researchobjective_set.add(objective)
            self.save()

        return objective

    @property
    def conference(self):
        objective = self.researchobjective_set.filter(name=ResearchObjective.CONFERENCE, complete=False).first()
        if not objective:
            objective = ResearchObjective.create(ResearchObjective.CONFERENCE, self)
            objective.save()
            self.researchobjective_set.add(objective)
            self.save()

        return objective

    @property
    def journal(self):
        objective = self.researchobjective_set.filter(name=ResearchObjective.JOURNAL, complete=False).first()
        if not objective:
            objective = ResearchObjective.create(ResearchObjective.JOURNAL, self)
            objective.save()
            self.researchobjective_set.add(objective)
            self.save()

        return objective

    @property
    def can_move(self):
        return not self.playertick_set.filter(tick=self.game.current_tick)

    @property
    def remaining_moves(self):
        return self.game._ticks - self.playertick_set.count()


def set_player_defaults(sender, instance, **kwargs):

    if instance.number == 0:
        instance.number = instance.game.player_set.count()
        instance.save()

    if not hasattr(instance, 'vulnerabilities'):
        Vulnerabilities.create(instance)

    if not hasattr(instance, 'capabilities'):
        Capabilities.create(instance)

    if not instance.researchobjective_set.all():
        for objective in ResearchObjective.get_initial_set(instance):
            instance.researchobjective_set.add(objective)

post_save.connect(set_player_defaults, sender=Player)


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
    player = models.ForeignKey(Player)
    research_resources = models.ManyToManyField(ResearchResource)
    value = models.IntegerField(null=True, blank=True)
    deadline = models.IntegerField(null=True, blank=True)  # deadline not in use yet
    complete = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s Objective' % (self.get_name_display().capitalize())

    # Creates and saves a ResearchObjective object of the provided name parameter
    @classmethod
    def create(cls, name, player):
        research_objective = cls(name=name, value=name*10, player=player)   # Fix value for each objective
        research_objective.save()
        for i in range(name):
            research_resource = ResearchResource.create()
            research_objective.research_resources.add(research_resource)

        research_objective.save()
        return research_objective

    # Returns a set of objects containing one of each Reserarch Objective types
    @classmethod
    def get_initial_set(self, player):
        research_objective_set = []
        for (x, y) in self.RESEARCH_OBJECTIVES:
            new_objective = self.create(x, player)
            research_objective_set.append(new_objective)

        return research_objective_set


''' A Security Resource for protecting against an Attack '''
class SecurityResource(models.Model):
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s Security Resource' % (self.get_classification_display().capitalize())

    @classmethod
    def create(cls, classification):
        security_resource = cls(classification=classification)
        security_resource.save()
        return security_resource


''' A player's set of capabilities '''
class Capabilities(models.Model):

    security_resources = models.ManyToManyField(SecurityResource)
    player = models.OneToOneField(Player, null=True)

    def __unicode__(self):
        if hasattr(Capabilities, 'player'):
            return u'%s\'s Capabilities' % (self.player.name)

    @classmethod
    def create(cls, player):
        capabilities = cls(player=player)
        capabilities.save()
        for (x,y) in RESOURCE_CLASSIFICATIONS:
            security_resource = SecurityResource.create(x)
            capabilities.security_resources.add(security_resource)

        capabilities.save()
        return capabilities


''' A player's set of vulnerabilities '''
class Vulnerabilities(models.Model):

    security_resources = models.ManyToManyField(SecurityResource)
    player = models.OneToOneField(Player, null=True)

    def __unicode__(self):
        if hasattr(Vulnerabilities, 'player'):
            return u'%s\'s Vulnerabilities' % (self.player.name)

    @classmethod
    def create(cls, player):
        vulnerabilities = cls(player=player)
        vulnerabilities.save()
        for (x,y) in RESOURCE_CLASSIFICATIONS:
            security_resource = SecurityResource.create(x)
            vulnerabilities.security_resources.add(security_resource)

        vulnerabilities.save()
        return vulnerabilities



''' An Attack Resource for issuing an attack against a Research Resource '''
class AttackResource(models.Model):
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS)

    def __unicode__(self):
        return u'%s Attack Resource' % (self.get_classification_display().capitalize())

    @classmethod
    def create(cls, game):
        if game.tick_set.count() > 1:
            num_ticks = game.tick_set.count()
            attack_probability = game.tick_set.get(number=(num_ticks - 1)).next_attack_probability
            blue, yellow, red = attack_probability.blue, attack_probability.yellow, attack_probability.red
            attack_probability = [(0, blue, BLUE),
                                                (blue, blue+red, RED),
                                                (blue+red, blue+red+yellow, YELLOW)]
            rand = random.randint(1,100)
            for lo, hi, classification in attack_probability:
                if rand >= lo and rand < hi:
                    print rand
                    attack_resource = cls(classification=classification)
                    attack_resource.save()
                    return attack_resource

            # Shouldn't reach here.  Returns random classification
            return cls(classification=random.randint(BLUE,YELLOW))


''' The probability per classification of an AttackResource object in the next round '''
class AttackProbability(models.Model):
    blue = models.IntegerField()
    yellow = models.IntegerField()
    red = models.IntegerField()

    def __unicode__(self):
        return u'blue: %s, red: %s, yellow: %s' %(self.blue, self.red, self.yellow)

    @classmethod
    def create(cls):
        blue = random.randint(0, 100)
        yellow = random.randint(0, 100 - blue)
        red = (100 - yellow - blue)
        attack_probability = cls(blue=blue, yellow=yellow, red=red)
        attack_probability.save()
        return attack_probability


''' Tick object that keeps game state '''
class Tick(models.Model):
    number = models.IntegerField(default = 1)
    game = models.ForeignKey(Game)
    complete = models.BooleanField(default=False)
    attack = models.OneToOneField(AttackResource, null=True, default=None, related_name="attack")
    next_attack_probability = models.OneToOneField(AttackProbability)

    def __unicode__(self):
        return u'Tick %s of %s' % (self.number, self.game)

    @classmethod
    def create(cls, game):
        tick = cls(game=game)
        if game.tick_set.all():
            tick.number = game.tick_set.latest('number').number + 1
        tick.attack = AttackResource.create(game)
        tick.next_attack_probability = AttackProbability.create()
        tick.save()


''' An object for synchronizing players' moves within a round '''
class PlayerTick(models.Model):
    tick = models.ForeignKey(Tick)
    player = models.ForeignKey(Player)


def update_tick(sender, instance, **kwargs):
    game = instance.player.game
    players = Player.objects.filter(game=game)
    for player in players:
        if player.can_move:
            return

    Tick.create(game=game)

post_save.connect(update_tick, sender=PlayerTick)


''' Group Message object '''
class Message(models.Model):
    game = models.ForeignKey(Game, null=True, editable=False)
    created_by = models.ForeignKey(Player, null=True, editable=False)
    content = models.TextField(max_length=500, editable=False)

    def __unicode__(self):
        content = (self.content[:75] + '...') if len(self.content) > 25 else self.content
        if self.game and self.created_by:
            return u'Game #%s: %s said, \"%s\"' % (self.game.game_key,
                                                                        self.created_by.user.username,
                                                                        content)
        else:
            return u'%s' % content




