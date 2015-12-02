from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import models
from django.db.models.signals import post_save

from custom_models import IntegerRangeField
from datetime import timedelta
from random import choice
import random




''' The Game object for maintaining game state and players '''
class Game(models.Model):

    GAME_KEY_LENGTH = 5

    _ticks = models.IntegerField()
    game_key = models.CharField(max_length=GAME_KEY_LENGTH*2, unique=True, null=True, blank=True, editable=False)
    attack_frequency = IntegerRangeField(min_value=0, max_value=100)
    complete = models.BooleanField(default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

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
            return self.tick_set.last().attack
        else:
            return None

    @property
    def players(self):
        return self.player_set.all()


    def generate_random_alphanumeric(self, length=GAME_KEY_LENGTH):
        return str(Game.objects.count() + 1) + "x" + ''.join(random.choice('0123456789ABCDEF') for i in range(length))

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


''' A Player objec to hold player state '''
class Player(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    score = models.IntegerField(default=0, editable=False)
    number = models.IntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'%s in %s' % (self.user.username, self.game)

    @property
    def name(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    @property
    def workshop(self):
        objective = self.researchobjective_set.filter(name=ResearchObjective.WORKSHOP,
                                                                                    complete=False,
                                                                                    research_resources__isnull=False).first()
        if not objective:
            objective = ResearchObjective.create(ResearchObjective.WORKSHOP, self)
            objective.save()
            self.researchobjective_set.add(objective)
            self.save()

        return objective

    @property
    def conference(self):
        objective = self.researchobjective_set.filter(name=ResearchObjective.CONFERENCE,
                                                                                    complete=False,
                                                                                    research_resources__isnull=False).first()
        if not objective:
            objective = ResearchObjective.create(ResearchObjective.CONFERENCE, self)
            objective.save()
            self.researchobjective_set.add(objective)
            self.save()

        return objective

    @property
    def journal(self):
        objective = self.researchobjective_set.filter(name=ResearchObjective.JOURNAL,
                                                                                    complete=False,
                                                                                    research_resources__isnull=False).first()
        if not objective:
            objective = ResearchObjective.create(ResearchObjective.JOURNAL, self)
            objective.save()
            self.researchobjective_set.add(objective)
            self.save()

        return objective

    @property
    def can_move(self):
        return not self.playertick_set.filter(tick=self.game.current_tick) and not self.game.complete

    @property
    def remaining_moves(self):
        return self.game._ticks - self.playertick_set.count()

    @property
    def sanctioned(self):
        if self.sanctionee.exists() and (self.sanctionee.latest("tick_number").tick_number == self.game.current_tick.number):
            return True
        else:
            return False


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
            return u'%s Resource' % (self.get_classification_display().capitalize())

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s Objective' % (self.get_name_display().capitalize())

    # Creates and saves a ResearchObjective object of the provided name parameter
    @classmethod
    def create(cls, name, player):

        # Assign appropriate values to Research Objectives
        value = 0
        if name == 1:
            value = 10
        elif name == 2:
            value = 25
        elif name == 3:
            value = 45

        research_objective = cls(name=name, value=value, player=player)   # Fix value for each objective
        research_objective.save()
        for i in range(name):
            research_resource = ResearchResource.create()
            research_objective.research_resources.add(research_resource)

        research_objective.save()
        return research_objective

    # Returns a set of objects containing one of each Reserarch Objective types
    @classmethod
    def get_initial_set(cls, player):
        research_objective_set = []
        for (x, y) in cls.RESEARCH_OBJECTIVES:
            new_objective = cls.create(x, player)
            research_objective_set.append(new_objective)

        return research_objective_set


''' A Security Resource for protecting against an Attack '''
class SecurityResource(models.Model):
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s Attack Resource' % (self.get_classification_display().capitalize())

    @classmethod
    def deactivate_security(cls, player, attack_resource):
        v = player.vulnerabilities
        r = v.security_resources.get(classification=attack_resource.classification)
        if r.active:
            r.active = False
            r.save()
            return True
        else:
            c = Capabilities.objects.get(player=player).security_resources.get(classification=attack_resource.classification)
            c.active = False;
            c.save()
            return False


    @classmethod
    def incomplete_research(cls, player, attack_resource):
        for ro in player.researchobjective_set.filter(complete=False):
            for r in ro.research_resources.all():
                if r.classification == attack_resource.classification:
                    r.complete=False
                    r.save()
        return True


    @classmethod
    def create(cls, game):
        if game.tick_set.count() > 0 and (random.randint(0,100) < game.attack_frequency):
            num_ticks = game.tick_set.count()
            attack_probability = game.tick_set.get(number=num_ticks).next_attack_probability
            blue, yellow, red = attack_probability.blue, attack_probability.yellow, attack_probability.red
            attack_probability = [(0, blue, BLUE),
                                                (blue, blue+red, RED),
                                                (blue+red, blue+red+yellow, YELLOW)]
            rand = random.randint(1,100)
            for lo, hi, classification in attack_probability:
                if rand >= lo and rand < hi:
                    attack_resource = cls(classification=classification)
                    attack_resource.save()
                    break

            for player in game.player_set.all():
                if not cls.deactivate_security(player, attack_resource):
                    cls.incomplete_research(player, attack_resource)

            return attack_resource


''' The probability per classification of an AttackResource object in the next round '''
class AttackProbability(models.Model):
    blue = models.IntegerField()
    yellow = models.IntegerField()
    red = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Tick %s of %s' % (self.number, self.game)

    @classmethod
    def create(cls, game):
        if not game.complete:
            tick = cls(game=game)
            if game.tick_set.all():
                tick.number = game.tick_set.latest('number').number + 1
            tick.attack = AttackResource.create(game)
            tick.next_attack_probability = AttackProbability.create()
            tick.save()

            # Take away  player's turned
            sanctions = Sanction.objects.filter(tick_number=tick.number)
            if sanctions:
                for sanction in sanctions:
                        PlayerTick(tick=tick, player=sanction.sanctionee).save()

            return tick


''' An object for synchronizing players' moves within a round '''
class PlayerTick(models.Model):
    tick = models.ForeignKey(Tick)
    player = models.ForeignKey(Player)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def update_tick(sender, instance, **kwargs):
    game = instance.player.game
    players = Player.objects.filter(game=game)
    for player in players:
        if player.can_move:
            return

    t = game.tick_set.last()
    t.complete = True
    t.save()
    Tick.create(game=game)

post_save.connect(update_tick, sender=PlayerTick)


''' Group Message object '''
class Message(models.Model):
    game = models.ForeignKey(Game, null=True, editable=False)
    created_by = models.ForeignKey(Player, null=True, editable=False)
    content = models.TextField(max_length=500, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        content = (self.content[:75] + '...') if len(self.content) > 25 else self.content
        if self.game and self.created_by:
            return u'Game #%s: %s said, \"%s\"' % (self.game.game_key,
                                                                        self.created_by.user.username,
                                                                        content)
        else:
            return u'%s' % content


class Sanction(models.Model):
    sanctioner = models.ForeignKey(Player, related_name="sanctioner")
    sanctionee = models.ForeignKey(Player, related_name="sanctionee")
    tick_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s sanctioned %s' %(self.sanctioner.user.username, self.sanctionee.user.username)

    @classmethod
    def create(cls, sanctioner, sanctionee, tick):
        sanction = cls(sanctioner=sanctioner, sanctionee=sanctionee, tick_number=(tick.number + 1))
        sanction.save()
        return sanction


