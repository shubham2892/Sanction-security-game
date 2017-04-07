import json
import random

from channels import Group
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import apnumber
from django.db import IntegrityError
from django.db import models
from django.db.models.signals import post_save

from custom_models import IntegerRangeField

#### GLOBAL VARIABLES ####

''' Points earned by Research Objective'''
WORKSHOP_VALUE = 10
CONFERENCE_VALUE = 25
JOURNAL_VALUE = 45

NO_SANC = 0
INDIVIDUAL_SANC = 1
GROUP_SANC = 2

MANAGER_SANC = (
    (INDIVIDUAL_SANC, "Individual Sanction"),
    (GROUP_SANC, "Group Sanction"),
    (NO_SANC, "No Sanction"),
)

''' The Game object for maintaining game state and players '''


class Game(models.Model):
    GAME_KEY_LENGTH = 5

    _ticks = models.IntegerField()
    game_key = models.CharField(max_length=GAME_KEY_LENGTH * 2, unique=True, null=True, blank=True, editable=False)
    attack_frequency = IntegerRangeField(min_value=0, max_value=100)
    manager_sanc = models.IntegerField(choices=MANAGER_SANC, default=INDIVIDUAL_SANC)
    peer_sanc = models.BooleanField(default=True)
    complete = models.BooleanField(default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return u'Game #%s' % (self.game_key)

    # Game print override -- the main query for reading game data
    @property
    def results(self):
        s = 'Game #{}\n\n'.format(self.game_key)
        for tick in self.tick_set.filter(complete=True):
            s += "  #### Tick Number {} ####\n".format(tick.number)
            s += "  Attack: {} \n".format(tick.attack)
            s += "  Next Attack Probabilities: {}\n".format(tick.next_attack_probability)

            s += "\n    ## Player Actions ##\n"
            for player_tick in tick.playertick_set.all().order_by('player'):
                s += "    Player: Player {} ({}) \n".format(apnumber(player_tick.player.number).capitalize(),
                                                            player_tick.player.user.username)
                s += "      - Action: {} \n".format(player_tick.get_action_display())

            s += "\n    ## Messages ##\n"
            if tick.message_set.all():
                for message in tick.message_set.all():
                    if message.created_by:
                        s += "    Player {} says: \"{}\" at {} \n".format(
                            apnumber(message.created_by.number).capitalize(), message.content, message.created_at)
                    else:
                        s += "    ***Announcement***: \"{}\"\n".format(message.content)
            else:
                s += "    No messages.\n"

            s += '\n'

        return s

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
                if failures > 5:  # or some other arbitrary cutoff point at which things are clearly wrong
                    raise
                else:
                    # looks like a collision, try another random value
                    self.game_key = self.generate_random_alphanumeric()
            else:
                success = True

        # Create the first game tick
        if not self.tick_set.all():
            Tick.create_game_tick(game=self)


''' A Player object to hold player state '''


class Player(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    score = models.IntegerField(default=0, editable=False)
    props = models.IntegerField(default=0, editable=False)
    number = models.IntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    # the last tick the player lose each security resource vulnerability
    last_tick_blue = models.IntegerField(default=0, editable=False)
    last_tick_yellow = models.IntegerField(default=0, editable=False)
    last_tick_red = models.IntegerField(default=0, editable=False)

    # counts the number of ticks of sanctions in the current manager sanction
    counter = models.IntegerField(default=0, editable=False)
    # counts the supposed number of ticks of sanctions in the current manager sanction
    counter_sum = models.IntegerField(default=0, editable=False)

    # number of finished tasks
    nf_blue = models.IntegerField(default=0, editable=False)
    nf_yellow = models.IntegerField(default=0, editable=False)
    nf_red = models.IntegerField(default=0, editable=False)
    nf_workshop = models.IntegerField(default=0, editable=False)
    nf_conference = models.IntegerField(default=0, editable=False)
    nf_journal = models.IntegerField(default=0, editable=False)

    # security tasks that are not finished when the manager decided to sanction they player (value == False);
    # unfinished tasks are modified to be finished after manager sanction
    blue_status = models.BooleanField(default=True, editable=False)
    yellow_status = models.BooleanField(default=True, editable=False)
    red_status = models.BooleanField(default=True, editable=False)

    def __unicode__(self):
        return u'%s in %s' % (self.user.username, self.game)

    @property
    def name(self):
        return "{}".format(self.user.username)

    # A player's active workshop objective; creates a new one if need be
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

    # A player's active conference objective; creates a new one if need be
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

    # A player's active journal objective; creates a new one if need be
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
    def deadline_sanction_blue(self):
        if self.game.peer_sanc:
            return 4 - (self.game.current_tick - self.last_tick_blue)
        else:
            return 6 - (self.game.current_tick - self.last_tick_blue)

    @property
    def deadline_sanction_red(self):
        if self.game.peer_sanc:
            return 4 - (self.game.current_tick - self.last_tick_red)
        else:
            return 6 - (self.game.current_tick - self.last_tick_red)

    @property
    def deadline_sanction_yellow(self):
        if self.game.peer_sanc:
            return 4 - (self.game.current_tick - self.last_tick_yellow)
        else:
            return 6 - (self.game.current_tick - self.last_tick_yellow)

    # Returns true if a player can make a move at a given instance;
    @property
    def can_move(self):
        return not self.playertick_set.filter(
            tick=self.game.current_tick).exists() and not self.game.complete

    # Returns true if the player clicked the pass button
    @property
    def passed(self):
        return self.playertick_set.filter(tick=self.game.current_tick, action=PASS) and not self.game.complete

    # Returns true if the manager just decided to sanction this player last tick
    @property
    def tick_just_sanctioned(self):
        return self.last_tick + 1 == self.game.current_tick.number and not self.game.complete

    # Returns the total number of remaining  moves for a player with a game instance
    @property
    def remaining_moves(self):
        return self.game._ticks - self.playertick_set.count()

    # Returns true if a player is peer sanctioned at a given instance
    @property
    def sanctioned(self):
        current_tick = self.game.current_tick.number
        if self.sanctionee.exists() and self.sanctionee.filter(tick_number=current_tick, game=self.game).exists():
            return True
        else:
            return False

    # Returns true if a player is sanctioned by the manager at a given instance
    @property
    def manager_sanctioned(self):
        current_tick = self.game.current_tick.number
        if self.sanctionee_by_manager.exists() and (
                self.sanctionee_by_manager.filter(tick_number=current_tick, game=self.game).exists()):
            return True
        else:
            return False

    # Returns an integer value describing a players' rank based on current score
    @property
    def rank(self):
        rank = Player.objects.filter(game=self.game, score__gt=self.score).count() + 1
        return rank

    def number_of_vulnerabilities(self):
        vulnerabilities = self.vulnerabilities.security_resources.all()
        return vulnerabilities.filter(active=False).count()


# Set's a player's default values, called as a post_save signal
def set_player_defaults(sender, instance, **kwargs):
    if sender == Player:
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
LAB = 4

RESOURCE_CLASSIFICATIONS = (
    (BLUE, "blue"),
    (RED, "red"),
    (YELLOW, "yellow"),
    (LAB, "lab"),
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
        research_resource = cls(classification=random.randint(1, 3))
        research_resource.save()
        return research_resource


''' A Research Task comprised of some number of Research Resources '''


class ResearchObjective(models.Model):
    # Research Objective types
    WORKSHOP = 1
    CONFERENCE = 2
    JOURNAL = 3

    RESEARCH_OBJECTIVES = (
        (WORKSHOP, "workshop"),
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
        if name == cls.WORKSHOP:
            value = WORKSHOP_VALUE
        elif name == cls.CONFERENCE:
            value = CONFERENCE_VALUE
        elif name == cls.JOURNAL:
            value = JOURNAL_VALUE

        research_objective = cls(name=name, value=value, player=player)
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
        if self.active:
            return u'Active %s Security Resource' % (self.get_classification_display().capitalize())
        else:
            return u'Inactive %s Security Resource' % (self.get_classification_display().capitalize())

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
        for (x, y) in RESOURCE_CLASSIFICATIONS:
            if not x == LAB:
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
        for (x, y) in RESOURCE_CLASSIFICATIONS:
            if not x == LAB:
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
    def deactivate_security(cls, player, attack_class):
        v = player.vulnerabilities
        r = v.security_resources.get(classification=attack_class)
        if r.active:
            r.active = False
            r.save()
            return True
        else:
            c = Capabilities.objects.get(player=player).security_resources.get(classification=attack_class)
            c.active = False
            c.save()
            return False

    @classmethod
    def incomplete_research(cls, player, attack_class):
        for ro in player.researchobjective_set.filter(complete=False):
            for r in ro.research_resources.all():
                if r.classification == attack_class:
                    r.complete = False
                    r.save()
        return True

    @classmethod
    def create(cls, game):
        # If it's not the first round of the game (we don't want to attack on the first round...)
        if game.tick_set.count() > 0:

            # If an attack occurs, given the game's constant attack frequency (see Game.attack_frequency)
            if random.randint(0, 100) < game.attack_frequency:

                # Check first to see if a LAB attack occurs
                # A lab attack will occur only as frequent as any other attack (i.e. is dictated by attack_frequency)
                # Querying all players' vulnerabilities to compare active v. inactive
                num_inactive = 0
                total = 0
                for player in game.player_set.all():
                    vulnerabilities = player.vulnerabilities.security_resources.all()
                    num_inactive += vulnerabilities.filter(active=False).count()
                    total += vulnerabilities.count()

                # The probability of a LAB attack is the total number of inactive vulnerabilities
                # of all players over the total number of vulnerabilities of all players
                prob_LAB_attack = float(num_inactive) / float(total) * 100
                print "LAB attack probability: %s" % prob_LAB_attack

                # If random number between 1 and 100 is less than probability of LAB attack, then LAB attack occurs
                if random.randint(0, 100) < prob_LAB_attack:
                    attack_resource = cls(classification=LAB)
                    attack_resource.save()
                    content = "Lab attack occurred at tick:{}".format(game.ticks)
                    message = Message(content=content, game=game, tick=game.current_tick, created_by=None)
                    message.save()

                    # If attack occurs, perform the attack.
                    for player in game.player_set.all():
                        if not player.sanctioned and not player.manager_sanctioned:
                            for resource in player.vulnerabilities.security_resources.all():
                                if not cls.deactivate_security(player, resource.classification):
                                    cls.incomplete_research(player, resource.classification)

                # Else, a regular attack occurs, and now we determine which color
                # Each color has a probabillity of occurring that was established the previous round
                else:
                    num_ticks = game.tick_set.count()
                    attack_probability = game.tick_set.get(number=num_ticks).next_attack_probability
                    blue, yellow, red = attack_probability.blue, attack_probability.yellow, attack_probability.red
                    attack_probability = [(0, blue, BLUE),
                                          (blue, blue + red, RED),
                                          (blue + red, blue + red + yellow, YELLOW)]
                    rand = random.randint(1, 99)
                    for lo, hi, classification in attack_probability:
                        if lo <= rand < hi:
                            attack_resource = cls(classification=classification)
                            attack_resource.save()
                            content = "{} attack occurred at tick:{}".format(
                                RESOURCE_CLASSIFICATIONS[classification - 1][1], game.ticks)
                            message = Message(content=content, game=game, tick=game.current_tick, created_by=None)
                            message.save()
                            break

                    # Once the color of the attack is determined, perform the attack on the player
                    for player in game.player_set.all():
                        if not player.sanctioned and not player.manager_sanctioned:
                            if not cls.deactivate_security(player, attack_resource.classification):
                                cls.incomplete_research(player, attack_resource.classification)

                return attack_resource


''' The probability per classification of an AttackResource object in the next round '''


class AttackProbability(models.Model):
    blue = models.IntegerField()
    yellow = models.IntegerField()
    red = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'blue: %s, red: %s, yellow: %s' % (self.blue, self.red, self.yellow)

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
    number = models.IntegerField(default=1)
    game = models.ForeignKey(Game)
    complete = models.BooleanField(default=False)
    attack = models.OneToOneField(AttackResource, null=True, default=None, related_name="attack")
    next_attack_probability = models.OneToOneField(AttackProbability)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Tick %s of %s' % (self.number, self.game)

    def manager_sanction(self):
        # A threshold (the number of ticks), for how long a vulnerability hasn't fixed would be taken into account
        # when considering the probability of manager sanction
        if self.game.peer_sanc:
            THRESHOLD = 6
        else:
            THRESHOLD = 4

        num_of_resource = 3
        # individual sanction
        if self.game.manager_sanc == 1:
            players = Player.objects.filter(game=self.game)

            for player in players:

                print "player %s in manager_sanction function" % (player.user.username)
                # if status == False, corresponding security task satisfy the condition of being counted in the prob. of manager sanction
                # blue
                resource = player.vulnerabilities.security_resources.get(classification=1)
                if resource.active:
                    player.last_tick_blue = self.number

                # red
                resource = player.vulnerabilities.security_resources.get(classification=2)
                if resource.active:
                    player.last_tick_red = self.number

                    # yellow
                resource = player.vulnerabilities.security_resources.get(classification=3)
                if resource.active:
                    player.last_tick_yellow = self.number

                player.save()

                if not player.manager_sanctioned and not player.sanctioned:
                    t_blue_status = True
                    t_red_status = True
                    t_yellow_status = True

                    count = 0
                    # blue
                    resource = player.vulnerabilities.security_resources.get(classification=1)
                    if not resource.active:
                        # to record the status of blue security task
                        t_blue_status = False
                        if self.number - player.last_tick_blue >= THRESHOLD:
                            count = count + 1

                    # print resource
                    # print "for blue: last tick is %s, count is %s" %(player.last_tick_blue, count)

                    # red
                    resource = player.vulnerabilities.security_resources.get(classification=2)
                    if not resource.active:
                        t_red_status = False
                        if self.number - player.last_tick_red >= THRESHOLD:
                            count = count + 1

                    # print resource
                    # print "for red: last tick is %s, count is %s" %(player.last_tick_red, count)

                    # yellow
                    resource = player.vulnerabilities.security_resources.get(classification=3)
                    if not resource.active:
                        t_yellow_status = False
                        if self.number - player.last_tick_yellow >= THRESHOLD:
                            count = count + 1

                    # print resource
                    # print "for yellow: last tick is %s, count is %s" %(player.last_tick_yellow, count)


                    sanction_prob = 1.0 * count / num_of_resource
                    # manager_obs_random = random.random()
                    # print "individual sanction probability is %s" %(sanction_prob)
                    x = random.random()
                    # print "random number is %s" %(x)

                    if x < sanction_prob:
                        print "The manager decided to sanction..."
                        # sanction the player for "2 * count" number of ticks
                        num_of_vul = player.number_of_vulnerabilities()
                        diff = self.game._ticks - self.number

                        ManagerSanction.create(player, self, num_of_vul * 2)
                        player.blue_status = t_blue_status
                        player.red_status = t_red_status
                        player.yellow_status = t_yellow_status
                        player.counter_sum = 2 * num_of_vul
                        player.save()

                        message_text = "%s is sanctioned by the lab manager for %s tick(s) at tick" % (
                            player.user.username, num_of_vul * 2)

                        for i in range(1, num_of_vul * 2 + 1):
                            if diff - i >= 0:
                                message_text += " %s" % (diff - i)

                        message = Message(content=message_text, created_by=None, game=self.game, tick=self)
                        message.save()

        # group sanction, fill in later
        elif self.game.manager_sanc == 2:
            players = Player.objects.filter(game=self.game)
            is_a_player_sanctioned = False
            for player in players:
                print " "
                print "At tick %s" % (self.number)
                print "player %s in manager_sanction function" % (player.user.username)
                # if status == False, corresponding security task satisfy the condition of being counted in the prob. of manager sanction
                # blue
                resource = player.vulnerabilities.security_resources.get(classification=1)
                if resource.active == True:
                    player.last_tick_blue = self.number

                # red
                resource = player.vulnerabilities.security_resources.get(classification=2)
                if resource.active == True:
                    player.last_tick_red = self.number

                    # yellow
                resource = player.vulnerabilities.security_resources.get(classification=3)
                if resource.active == True:
                    player.last_tick_yellow = self.number

                player.save()

                if not player.manager_sanctioned and not player.sanctioned:
                    t_blue_status = True
                    t_red_status = True
                    t_yellow_status = True

                    count = 0
                    # blue
                    resource = player.vulnerabilities.security_resources.get(classification=1)
                    if resource.active == False:
                        # to record the status of blue security task
                        t_blue_status = False
                        if self.number - player.last_tick_blue >= THRESHOLD:
                            count = count + 1

                    # print resource
                    # print "for blue: last tick is %s, count is %s" %(player.last_tick_blue, count)

                    # red
                    resource = player.vulnerabilities.security_resources.get(classification=2)
                    if resource.active == False:
                        t_red_status = False
                        if self.number - player.last_tick_red >= THRESHOLD:
                            count = count + 1

                    # print resource
                    # print "for red: last tick is %s, count is %s" %(player.last_tick_red, count)

                    # yellow
                    resource = player.vulnerabilities.security_resources.get(classification=3)
                    if resource.active == False:
                        t_yellow_status = False
                        if self.number - player.last_tick_yellow >= THRESHOLD:
                            count = count + 1

                    # print resource
                    # print "for yellow: last tick is %s, count is %s" %(player.last_tick_yellow, count)


                    sanction_prob = 1.0 * count / num_of_resource
                    # print "individual sanction probability is %s" %(sanction_prob)
                    x = random.random()
                    # print "random number is %s" %(x)

                    if x < sanction_prob:
                        is_a_player_sanctioned = True
                        num_of_vul = player.number_of_vulnerabilities()
                        break

            if is_a_player_sanctioned:
                for player in players:
                    # sanction the player for "2 * count" number of ticks

                    diff = self.game._ticks - self.number

                    ManagerSanction.create(player, self, num_of_vul * 2)
                    player.blue_status = t_blue_status
                    player.red_status = t_red_status
                    player.yellow_status = t_yellow_status
                    player.counter_sum = 2 * num_of_vul
                    player.save()

                    message_text = "Created Manager Sanction: Player %s is sanctioned by the lab manager for %s tick(s) at tick" % (
                        apnumber(player.number).capitalize(), num_of_vul * 2)

                    for i in range(1, num_of_vul * 2 + 1):
                        if diff - i >= 0:
                            message_text += " %s" % (diff - i)

                    message = Message(content=message_text, created_by=None, game=self.game, tick=self)
                    message.save()

        # no sanction, do nothing
        elif self.game.manager_sanc == 0:
            pass

    @classmethod
    def create_game_tick(cls, game):
        tick = cls(game=game)
        if game.tick_set.all():
            tick.number = game.tick_set.latest('number').number + 1
        tick.attack = AttackResource.create(game)
        tick.next_attack_probability = AttackProbability.create()
        tick.save()

        # Notifying all the players of tick complete
        attack_classification = ""
        players = Player.objects.filter(game=tick.game)

        if tick.attack:
            attack_classification = tick.attack.get_classification_display()
            for player in players:
                attack_items = {"immunity": [], "capability": []}
                for immnunity in player.vulnerabilities.security_resources.all():
                    if not immnunity.active:
                        attack_items["immunity"].append(immnunity.get_classification_display())
                for capability in player.capabilities.security_resources.all():
                    if not capability.active:
                        attack_items["capability"].append(capability.get_classification_display())
                attack_dictionary = {"type": "attack_type_update", "attack_item": attack_items}
                Group(str(player.pk)).send({"text": json.dumps(attack_dictionary)})

        tick.manager_sanction()
        tick_object = {"type": "tick_complete", "new_tick_count": game.ticks, "attack": attack_classification}
        Group("players").send({"text": json.dumps(tick_object)})


        # For every tick player specific updates
        player_tick_dictionary_list = []
        for player in players:
            sanction_threshold = [0, 0, 0]
            immunity_ids  = [-1, -1, -1]
            resource = player.vulnerabilities.security_resources.get(classification=BLUE)
            if not resource.active:
                sanction_threshold[0] = player.deadline_sanction_blue
                immunity_ids[0] = resource.pk

            resource = player.vulnerabilities.security_resources.get(classification=RED)
            if not resource.active:
                sanction_threshold[1] = player.deadline_sanction_red
                immunity_ids[1] = resource.pk

            resource = player.vulnerabilities.security_resources.get(classification=YELLOW)
            if not resource.active:
                sanction_threshold[2] = player.deadline_sanction_yellow
                immunity_ids[2] = resource.pk

            player_tick_dictionary = {"sanctioned": str(player.manager_sanctioned or player.sanctioned),
                                      "sanction_threshold": sanction_threshold,
                                      "immunity_ids": immunity_ids, "player_id":player.pk}
            player_tick_dictionary_list.append(player_tick_dictionary)

        player_tick_dictionarys = {"type": "sanction_status","sanction_dict":player_tick_dictionary_list}
        Group("players").send({"text": json.dumps(player_tick_dictionarys)})

        return tick

    @classmethod
    def create(cls, game):
        if game.ticks > 0:
            return cls.create_game_tick(game)
        else:
            # Game Over
            game.complete = True
            game.save()
            tick_object = {"type": "tick_complete", "new_tick_count": -1, "attack": ""}
            Group("players").send({"text": json.dumps(tick_object)})


''' PLAYER ACTIONS '''
REST = 0
SANCTION = 1
SECURITY = 2
RESEARCH_TASK = 3
RESEARCH_OBJ = 4
PASS = 5

ACTIONS = (
    (REST, "The player did not move."),
    (SANCTION, "sanctioned player"),
    (SECURITY, "activated security resource"),
    (RESEARCH_TASK, "completed research task"),
    (RESEARCH_OBJ, "completed research objective"),
    (PASS, "clicked the pass button")
)

''' An object for synchronizing players' moves within a round '''


class PlayerTick(models.Model):
    tick = models.ForeignKey(Tick)
    player = models.ForeignKey(Player)
    action = models.IntegerField(choices=ACTIONS, default=REST)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def update_tick(sender, instance, **kwargs):
    print "update tick called"
    game = instance.player.game
    players = Player.objects.filter(game=game)
    if not instance.player.can_move:
        print "sending move made notification"
        tick_object = {"type": "move_made", "move": "true"}
        Group(str(instance.player.pk)).send({"text": json.dumps(tick_object)})

    for player in players:
        if player.can_move:
            print "returning because other players can move"
            return

    t = game.tick_set.last()
    t.complete = True
    t.save()
    Tick.create(game=game)


post_save.connect(update_tick, sender=PlayerTick)


def __unicode__(self):
    return u'Tick #%s, %s, %s' % (self.tick, self.player, self.action)


''' Group Message object '''


class Message(models.Model):
    game = models.ForeignKey(Game, null=True, editable=False)
    tick = models.ForeignKey(Tick, null=True, editable=False)
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


def send_message_to_frontend(sender, instance, **kwargs):
    if sender == Message:
        message = {"message": instance.content, "type": "update_message_board"}
        Group("players").send({"text": json.dumps(message)})


post_save.connect(send_message_to_frontend, sender=Message)


class Sanction(models.Model):
    sanctioner = models.ForeignKey(Player, related_name="sanctioner")
    sanctionee = models.ForeignKey(Player, related_name="sanctionee")
    tick_number = models.IntegerField()
    game = models.ForeignKey(Game, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s sanctioned %s in game %s' % (
            self.sanctioner.user.username, self.sanctionee.user.username, self.sanctionee.game.game_key)

    @classmethod
    def create(cls, sanctioner, sanctionee, tick):
        sanction = cls(sanctioner=sanctioner, sanctionee=sanctionee, tick_number=(tick.number + 1), game=tick.game)
        sanction.save()
        return sanction


class ManagerSanction(models.Model):
    sanctionee = models.ForeignKey(Player, related_name="sanctionee_by_manager")
    tick_number = models.IntegerField()
    game = models.ForeignKey(Game, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Created manager sanction: %s for tick %s' % (self.sanctionee.user.username, self.tick_number)

    # the sanctionee is sanctioned for num_of_ticks_sanc ticks
    # create num_of_ticks_sanc ManagerSanction records
    @classmethod
    def create(cls, sanctionee, tick, num_of_ticks_sanc):
        # print "%s number of sanction(s):" %(num_of_ticks_sanc)
        # a player gets sanctioned by the manager twice the time of what his unfinished vulnerabilities are
        for i in range(1, num_of_ticks_sanc + 1):
            sanction = cls(sanctionee=sanctionee, tick_number=(tick.number + i), game=tick.game)
            sanction.save()


WORKSHOP_TASK = 0
CONFERENCE_TASK = 1
JOURNAL_TASK = 2
RED_TASK = 3
YELLOW_TASK = 4
BLUE_TASK = 5

TASK_TYPES = (
    (WORKSHOP_TASK, "Workshop Research Task"),
    (CONFERENCE_TASK, "Conference Research Task"),
    (JOURNAL_TASK, "Journal Research Task"),
    (RED_TASK, "Red Security Task"),
    (YELLOW_TASK, "Yellow Security Task"),
    (BLUE_TASK, "Blue Security Task")
)


class Statistics(models.Model):
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player, default=None)
    player_tick = models.ForeignKey(PlayerTick, default=None)
    # number of finished tasks
    nf_finished_task = models.IntegerField(default=0)
    # type of task
    type_of_task = models.IntegerField(choices=TASK_TYPES, default=None)

    def __unicode__(self):
        return u'In game %s, %s finished %s at tick %s. Total number of finished task of this type is %s' % (
            self.game.game_key, self.player.user.username, self.get_type_of_task_display(),
            self.player_tick.tick.number,
            self.nf_finished_task)
