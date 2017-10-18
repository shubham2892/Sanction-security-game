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


# class PlayerManager(models.Manager):
#     def create(self, **obj_data):
#         Workshop.objects.create(player=self.pk)
#         Conference.objects.create(player=self.pk)
#         Journal.objects.create(player=self.pk)
#         return super(PlayerManager, self).create(**obj_data)


class Player(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    score = models.IntegerField(default=0, editable=False)
    number = models.IntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    # the last tick the player lose each security resource vulnerability
    last_tick_blue = models.IntegerField(default=0, editable=False)
    last_tick_yellow = models.IntegerField(default=0, editable=False)
    last_tick_red = models.IntegerField(default=0, editable=False)

    # number of finished tasks
    nf_blue = models.IntegerField(default=0, editable=False)
    nf_yellow = models.IntegerField(default=0, editable=False)
    nf_red = models.IntegerField(default=0, editable=False)
    nf_workshop = models.IntegerField(default=0, editable=False)
    nf_conference = models.IntegerField(default=0, editable=False)
    nf_journal = models.IntegerField(default=0, editable=False)

    # security tasks that are not finished when the manager decided to sanction they player (value == False);
    # unfinished tasks are modified to be finished after manager sanction
    blue_status_security = models.BooleanField(default=True, editable=False)
    yellow_status_security = models.BooleanField(default=True, editable=False)
    red_status_security = models.BooleanField(default=True, editable=False)

    blue_status_capability = models.BooleanField(default=True, editable=False)
    yellow_status_capability = models.BooleanField(default=True, editable=False)
    red_status_capability = models.BooleanField(default=True, editable=False)

    # objects = PlayerManager()

    def __unicode__(self):
        return u'%s in %s' % (self.user.username, self.game)

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
    #     if self.pk:
    #         Workshop.objects.create(player=self.pk)
    #         Conference.objects.create(player=self.pk)
    #         Journal.objects.create(player=self.pk)
    #     super(Player, self).save(force_insert, force_update, using, update_fields)

    @property
    def name(self):
        return "{}".format(self.user.username)

    @property
    def deadline_sanction_blue(self):
        if self.game.peer_sanc:
            return 3 - (self.last_tick_blue - self.game.ticks)
        else:
            return 6 - (self.game.current_tick.number - self.last_tick_blue)

    @property
    def deadline_sanction_blue_rep(self):
        if self.deadline_sanction_blue <= 0:
            return 'X'
        return self.deadline_sanction_blue

    @property
    def deadline_sanction_red(self):
        if self.game.peer_sanc:
            return 3 - (self.last_tick_red - self.game.ticks)
        else:
            return 6 - (self.game.current_tick.number - self.last_tick_red)

    @property
    def deadline_sanction_red_rep(self):
        if self.deadline_sanction_red <= 0:
            return 'X'
        return self.deadline_sanction_red

    @property
    def deadline_sanction_yellow(self):
        if self.game.peer_sanc:
            return 3 - (self.last_tick_yellow - self.game.ticks)
        else:
            return 6 - (self.game.current_tick.number - self.last_tick_yellow)

    @property
    def deadline_sanction_yellow_rep(self):
        if self.deadline_sanction_yellow <= 0:
            return 'X'
        return self.deadline_sanction_yellow

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
        print "checking for tick:{}".format(current_tick)
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
        count = 0
        if self.red_status_security:
            count += 1
        if self.yellow_status_security:
            count += 1
        if self.blue_status_security:
            count += 1
        return count

    def update_player_payload(self, player_payload):

        # Append Blue Security
        player_payload["blue_security"] = {"active": self.blue_status_security,
                                           "deadline_sanction": self.deadline_sanction_blue_rep}

        # Append Red Security
        player_payload["red_security"] = {"active": self.red_status_security,
                                          "deadline_sanction": self.deadline_sanction_red_rep}

        # Append Yellow Security
        player_payload["yellow_security"] = {"active": self.yellow_status_security,
                                             "deadline_sanction": self.deadline_sanction_yellow_rep}

        player_payload["blue_capability"] = self.blue_status_capability
        player_payload["red_capability"] = self.red_status_capability
        player_payload["yellow_capability"] = self.yellow_status_capability

        print player_payload


# Set's a player's default values, called as a post_save signal
def set_player_defaults(sender, instance, **kwargs):
    if sender == Player:
        if Workshop.objects.filter(player=instance).count() == 0:
            Workshop.objects.create(player=instance)
        if Conference.objects.filter(player=instance).count() == 0:
            Conference.objects.create(player=instance)
        if Journal.objects.filter(player=instance).count() == 0:
            Journal.objects.create(player=instance)


class GameSet(models.Model):
    user = models.ForeignKey(User)
    game_id1 = models.ForeignKey(Game, related_name="game_id1")
    game_id2 = models.ForeignKey(Game, related_name="game_id2")
    game_id3 = models.ForeignKey(Game, related_name="game_id3")
    demo_id = models.ForeignKey(Game, related_name="game_demo")
    consent_check = models.BooleanField(default=False)
    video_check = models.BooleanField(default=False)
    demo_check = models.BooleanField(default=False)
    g1_check = models.BooleanField(default=False)
    g2_check = models.BooleanField(default=False)
    g3_check = models.BooleanField(default=False)
    chat_link = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return u'Game #%s' % (self.user.username)


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


class Workshop(models.Model):
    player = models.ForeignKey(Player, related_name="workshop")
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS, default=BLUE)
    count = models.IntegerField(default=0)
    complete = models.BooleanField(default=False)
    score = models.IntegerField(default=10)

    @property
    def classification_display(self):
        return RESOURCE_CLASSIFICATIONS[self.classification - 1][1]


class Journal(models.Model):
    player = models.ForeignKey(Player, related_name="journal")
    count = models.IntegerField(default=0)
    classification_one = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS, default=RED)
    classification_two = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS, default=BLUE)
    classification_three = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS, default=YELLOW)
    complete_one = models.BooleanField(default=False)
    complete_two = models.BooleanField(default=False)
    complete_three = models.BooleanField(default=False)
    score = models.IntegerField(default=25)

    @property
    def classification_display_one(self):
        return RESOURCE_CLASSIFICATIONS[self.classification_one - 1][1]

    @property
    def classification_display_two(self):
        return RESOURCE_CLASSIFICATIONS[self.classification_two - 1][1]

    @property
    def classification_display_three(self):
        return RESOURCE_CLASSIFICATIONS[self.classification_three - 1][1]


class Conference(models.Model):
    player = models.ForeignKey(Player, related_name="conference")
    count = models.IntegerField(default=0)
    classification_one = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS, default=RED)
    classification_two = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS, default=BLUE)
    complete_one = models.BooleanField(default=False)
    complete_two = models.BooleanField(default=False)
    score = models.IntegerField(default=45)

    @property
    def classification_display_one(self):
        return RESOURCE_CLASSIFICATIONS[self.classification_one - 1][1]

    @property
    def classification_display_two(self):
        return RESOURCE_CLASSIFICATIONS[self.classification_two - 1][1]


''' An Attack Resource for issuing an attack against a Research Resource '''


class AttackResource(models.Model):
    classification = models.IntegerField(choices=RESOURCE_CLASSIFICATIONS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s Attack Resource' % (self.get_classification_display().capitalize())

    @classmethod
    def create(cls, game):
        # If it's not the first round of the game (we don't want to attack on the first round...)
        if game.tick_set.count() > 0:

            # If an attack occurs, given the game's constant attack frequency (see Game.attack_frequency)
            if random.randint(0, 100) < game.attack_frequency:

                # Check first to see if a LAB attack occurs
                # Probability of lab attack happening is one third the probability of normal lab attack

                num_ticks = game.tick_set.count()
                attack_probability = game.tick_set.get(number=num_ticks).next_attack_probability
                blue, yellow, red = attack_probability.blue, attack_probability.yellow, attack_probability.red
                attack_probability = [(0, blue, BLUE),
                                      (blue, blue + red, RED),
                                      (blue + red, blue + red + yellow, YELLOW),
                                      (blue + red + yellow, 99, LAB)
                                      ]

                rand = random.randint(0, 98)
                for lo, hi, classification in attack_probability:
                    if lo <= rand < hi:
                        attack_resource = cls(classification=classification)
                        attack_resource.save()
                        content = "{} attack occurred at tick:{}".format(
                            RESOURCE_CLASSIFICATIONS[classification - 1][1], game.ticks - 1)
                        message = Message(content=content, game=game, tick=game.current_tick, created_by=None)
                        message.save()
                        break

                # Once the color of the attack is determined, perform the attack on the player
                if attack_resource.classification == RED:
                    Player.objects.filter(game=game.id, red_status_security=False).update(red_status_capability=False)
                    Player.objects.filter(game=game.id, red_status_security=True).update(last_tick_red=game.ticks - 1)
                    Player.objects.filter(game=game.id).update(red_status_security=False)
                elif attack_resource.classification == YELLOW:
                    Player.objects.filter(game=game.id, yellow_status_security=False).update(
                        yellow_status_capability=False)
                    Player.objects.filter(game=game.id, yellow_status_security=True).update(
                        last_tick_yellow=game.ticks - 1)
                    Player.objects.filter(game=game.id).update(yellow_status_security=False)
                elif attack_resource.classification == BLUE:
                    Player.objects.filter(game=game.id, blue_status_security=False).update(blue_status_capability=False)
                    Player.objects.filter(game=game.id, blue_status_security=True).update(last_tick_blue=game.ticks - 1)
                    Player.objects.filter(game=game.id).update(blue_status_security=False)
                elif attack_resource.classification == LAB:
                    Player.objects.filter(game=game.id, red_status_security=False).update(red_status_capability=False)

                    Player.objects.filter(game=game.id, red_status_security=True).update(last_tick_red=game.ticks - 1)
                    Player.objects.filter(game=game.id, yellow_status_security=True).update(
                        last_tick_yellow=game.ticks - 1)
                    Player.objects.filter(game=game.id, blue_status_security=True).update(last_tick_blue=game.ticks - 1)

                    Player.objects.filter(game=game.id, yellow_status_security=False).update(
                        yellow_status_capability=False)
                    Player.objects.filter(game=game.id, blue_status_security=False).update(blue_status_capability=False)
                    Player.objects.filter(game=game.id).update(blue_status_security=False, yellow_status_security=False,
                                                               red_status_security=False)

                return attack_resource


''' The probability per classification of an AttackResource object in the next round '''


class AttackProbability(models.Model):
    blue = models.IntegerField()
    yellow = models.IntegerField()
    red = models.IntegerField()
    lab = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'blue: %s, red: %s, yellow: %s lab %s' % (self.blue, self.red, self.yellow, self.lab)

    @classmethod
    def create(cls):
        blue = random.randint(0, 100)
        yellow = random.randint(0, 100 - blue)
        red = random.randint(0, 100 - yellow - blue)
        lab = (100 - yellow - blue - red)
        attack_probability = cls(blue=blue, yellow=yellow, red=red, lab=lab)
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
        num_of_resource = 3
        # individual sanction
        if self.game.manager_sanc == 1:
            players = Player.objects.filter(game=self.game)

            for player in players:
                if not player.manager_sanctioned and not player.sanctioned:
                    count = 0
                    # Blue
                    if not player.blue_status_security:
                        # to record the status of blue security task
                        if player.deadline_sanction_blue <= 0:
                            count += 1

                    # Red
                    if not player.red_status_security:
                        if player.deadline_sanction_red <= 0:
                            count += 1

                    # Yellow
                    if not player.yellow_status_security:
                        if player.deadline_sanction_yellow <= 0:
                            count = count + 1

                    sanction_prob = 1.0 * count / num_of_resource
                    x = random.random()

                    if x < sanction_prob:
                        diff = self.game._ticks - self.number

                        ManagerSanction.create(player, self, count * 2)
                        message_text = "%s is sanctioned by the lab manager for %s tick(s) at tick" % (
                            player.user.username, count * 2)

                        for i in range(1, count * 2 + 1):
                            if diff - i >= 0:
                                message_text += " %s" % (diff - i)

                        message = Message(content=message_text, created_by=None, game=self.game, tick=self)
                        message.save()
                        # player.save()

        elif self.game.manager_sanc == 2:
            players = Player.objects.filter(game=self.game)
            is_a_player_sanctioned = False
            for player in players:
                if not player.manager_sanctioned and not player.sanctioned:
                    count = 0
                    # Blue
                    if not player.blue_status_security:
                        # to record the status of blue security task
                        if player.deadline_sanction_blue <= 0:
                            count += 1

                    # Red
                    if not player.red_status_security:
                        if player.deadline_sanction_red <= 0:
                            count += 1

                    # Yellow
                    if not player.yellow_status_security:
                        if player.deadline_sanction_yellow <= 0:
                            count = count + 1

                    sanction_prob = 1.0 * count / num_of_resource
                    # manager_obs_random = random.random()
                    x = random.random()

                    if x < sanction_prob:
                        is_a_player_sanctioned = True
                        break

            if is_a_player_sanctioned:
                for player in players:
                    diff = self.game._ticks - self.number

                    ManagerSanction.create(player, self, count * 2)
                    # player.counter_sum = 2 * count

                    message_text = "%s is sanctioned by the lab manager for %s tick(s) at tick" % (
                        player.user.username, count * 2)

                    for i in range(1, count * 2 + 1):
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
        tick.manager_sanction()

        # Notifying all the players of tick complete
        players = Player.objects.filter(game=tick.game)
        player_payload_list_json = {"type": "tick_complete"}
        player_payload_list = []
        for player in players:
            player_payload = {}
            player.update_player_payload(player_payload)
            player_payload["sanctioned"] = player.sanctioned or player.manager_sanctioned
            if tick.attack:
                player_payload["attack"] = tick.attack.get_classification_display()
            else:
                player_payload["attack"] = ""

            player_payload["new_tick_count"] = game.ticks
            player_payload["player_id"] = player.id
            player_payload["score"] = player.score
            player_payload_list.append(player_payload)

        player_payload_list_json["tick_payload"] = player_payload_list
        Group("players").send({"text": json.dumps(player_payload_list_json)})
        return tick

    @classmethod
    def create(cls, game):
        if game.ticks > 0:
            return cls.create_game_tick(game)
        else:
            # Game Over
            game.complete = True
            game.save()

            players = Player.objects.filter(game=game)
            player_payload_list_json = {"type": "tick_complete"}
            player_payload_list = []
            for player in players:
                player_payload = {}
                player.update_player_payload(player_payload)
                player_payload["sanctioned"] = False
                player_payload["attack"] = ""

                player_payload["new_tick_count"] = -1
                player_payload["player_id"] = player.id
                player_payload_list.append(player_payload)

            player_payload_list_json["tick_payload"] = player_payload_list
            Group("players").send({"text": json.dumps(player_payload_list_json)})


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
    game = instance.player.game
    players = Player.objects.filter(game=game)
    if not instance.player.can_move:
        tick_object = {"type": "move_made", "move": "true"}
        Group(str(instance.player.pk)).send({"text": json.dumps(tick_object)})

    for player in players:
        if player.can_move:
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
        # a player gets sanctioned by the manager twice the time of what his unfinished vulnerabilities are
        sanctions = []
        for i in range(0, num_of_ticks_sanc):
            sanction = cls(sanctionee=sanctionee, tick_number=(tick.number + i), game=tick.game)
            sanctions.append(sanction)
        ManagerSanction.objects.bulk_create(sanctions)


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
