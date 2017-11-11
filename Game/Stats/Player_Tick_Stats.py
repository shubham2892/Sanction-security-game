from collections import defaultdict

from Game.models import Game, Player, PlayerTick, Message, YELLOW, LAB, BLUE, RED, SECURITY_RED, PlayerTickDup, \
    SECURITY_BLUE, SECURITY_YELLOW


def parse_messages_for_attack(messages):
    attack_dict = defaultdict(lambda: 0)
    for message in messages:
        message_words = message.content.split()
        if message_words[0] == 'Yellow':
            tick_number = int(message_words[len(message_words) - 1].split(":")[1])
            attack_dict[tick_number] = YELLOW

        elif message_words[0] == 'Blue':
            tick_number = int(message_words[len(message_words) - 1].split(":")[1])
            attack_dict[tick_number] = BLUE

        elif message_words[0] == 'Red':
            tick_number = int(message_words[len(message_words) - 1].split(":")[1])
            attack_dict[tick_number] = RED
        elif message_words[0] == 'Lab':
            tick_number = int(message_words[len(message_words) - 1].split(":")[1])
            attack_dict[tick_number] = LAB

    return attack_dict


def parse_messages_for_sanction_manager(messages, username):
    sanction_dict = defaultdict(lambda: False)
    for message in messages:
        message_words = message.content.split()
        if message_words[0].lower() == username.lower():
            print message_words[0]
            if "Group Sanctioned" in message.content or "is Sanctioned" in message.content:
                # Individual Manager Sanction
                for message_word in reversed(message_words):
                    if message_word.isdigit():
                        sanction_dict[int(message_word)] = True
                    else:
                        break
    return sanction_dict


def parse_messages_for_peer_sanction(messages, username):
    sanction_dict = defaultdict(lambda: False)
    print username.lower()
    for message in messages:
        message_words = message.content.split()
        if message_words[4].lower() == username.lower():
            print message_words[0]
            if "has Sanctioned" in message.content:
                # Individual Manager Sanction
                for message_word in reversed(message_words):
                    if message_word.isdigit():
                        sanction_dict[int(message_word)] = True
                    else:
                        break
    return sanction_dict


def pertick_player_data():
    games = Game.objects.all()
    for game in games:
        message = Message.objects.filter(game=game)
        attack_dict = parse_messages_for_attack(message)

        players = Player.objects.filter(game=game)

        for player in players:
            player_sanction_manager_dict = parse_messages_for_sanction_manager(message, player.user.username)
            player_sanction_peer_dict = parse_messages_for_peer_sanction(message, player.user.username)
            player_ticks = PlayerTick.objects.filter(player=player).order_by("tick_number")
            red_immunity = True
            red_capability = True

            blue_immunity = True
            blue_capability = True

            yellow_immunity = True
            yellow_capability = True

            is_peer_sanction = False
            for player_tick in player_ticks:

                if player_sanction_peer_dict[player_tick.tick_number]:
                    is_peer_sanction = True
                else:
                    is_peer_sanction = False

                if (player_sanction_manager_dict[player_tick.tick_number - 1] is True and player_sanction_manager_dict[
                    player_tick.tick_number] is False):
                    red_immunity = True
                    red_capability = True
                    blue_capability = True
                    blue_immunity = True
                    yellow_capability = True
                    yellow_immunity = True

                if attack_dict[player_tick.tick_number] == RED:
                    red_immunity = False
                    attack_number = RED
                elif attack_dict[player_tick.tick_number] == BLUE:
                    blue_immunity = False
                    attack_number = BLUE
                elif attack_dict[player_tick.tick_number] == YELLOW:
                    yellow_immunity = False
                    attack_number = YELLOW
                elif attack_dict[player_tick.tick_number] == LAB:
                    yellow_immunity = False
                    blue_immunity = False
                    red_immunity = False
                    attack_number = LAB
                else:
                    attack_number = 0

                if not red_immunity:
                    red_capability = False

                if not yellow_immunity:
                    yellow_capability = False

                if not blue_immunity:
                    blue_capability = False

                if player_tick.action == SECURITY_RED:
                    red_immunity = True
                    red_capability = True

                if player_tick.action == SECURITY_BLUE:
                    blue_capability = True
                    blue_immunity = True

                if player_tick.action == SECURITY_YELLOW:
                    yellow_capability = True
                    yellow_immunity = True

                if (player_sanction_manager_dict[player_tick.tick_number]):
                    is_manager_sanction = True
                else:
                    is_manager_sanction = False

                PlayerTickDup.objects.create(tick_number=player_tick.tick_number, player=player,
                                             action=player_tick.action, is_red_security=red_immunity,
                                             is_blue_security=blue_immunity, is_blue_capability=blue_capability,
                                             is_yellow_security=yellow_immunity, is_yellow_capability=yellow_capability,
                                             is_red_capability=red_capability, is_attack=attack_number,
                                             is_peer_sanction=is_peer_sanction,
                                             is_manager_sanction=is_manager_sanction)
