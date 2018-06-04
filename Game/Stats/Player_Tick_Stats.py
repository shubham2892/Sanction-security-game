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
            # print message_words[0]
            if "Group Sanctioned" in message.content or "is Sanctioned" in message.content:
                # Individual Manager Sanction
                for message_word in reversed(message_words):
                    if message_word.isdigit():
                        sanction_dict[int(message_word)] = True
                    else:
                        break
    return sanction_dict


def parse_messages_for_peer_sanction(messages, username, player):
    sanction_dict = defaultdict(lambda: False)
    # print username.lower()
    indi_count = 0
    group_count = 0
    for message in messages:
        message_words = message.content.split()
        if message_words[0].lower() == username.lower():
        # print message_words[0]
            if "has Sanctioned" in message.content:
            # Individual Manager Sanction
            # for message_word in reversed(message_words):
            #     if message_word.isdigit():
            #         sanction_dict[int(message_word)] = True
                print username
                print message
                if player.game.manager_sanc == 1:
                    indi_count +=1
                    print "indi"
                else:
                    group_count +=1
                    print "group"
            # else:
            #     break

    return sanction_dict


def pertick_player_data():
    games = Game.objects.filter(id__lte=42)
    for game in games:
        message = Message.objects.filter(game=game)
        attack_dict = parse_messages_for_attack(message)

        players = Player.objects.filter(game=game)

        for player in players:
            player_sanction_manager_dict = parse_messages_for_sanction_manager(message, player.user.username)
            player_sanction_peer_dict = parse_messages_for_peer_sanction(message, player.user.username, player)
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
                else:
                    red_capability = True

                if not yellow_immunity:
                    yellow_capability = False
                else:
                    yellow_capability = True

                if not blue_immunity:
                    blue_capability = False
                else:
                    blue_capability = True

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

                # PlayerTickDup.objects.create(tick_number=player_tick.tick_number, player=player,
                #                              action=player_tick.action, is_red_security=red_immunity,
                #                              is_blue_security=blue_immunity, is_blue_capability=blue_capability,
                #                              is_yellow_security=yellow_immunity, is_yellow_capability=yellow_capability,
                #                              is_red_capability=red_capability, is_attack=attack_number,
                #                              is_peer_sanction=is_peer_sanction,
                #                              is_manager_sanction=is_manager_sanction)


def copy_player_ticks_dup():
    pertick_player_data()
    games = Game.objects.filter(id__gt=42)
    for game in games:
        message = Message.objects.filter(game=game)
        attack_dict = parse_messages_for_attack(message)

        players = Player.objects.filter(game=game)

        for player in players:
            player_ticks = PlayerTick.objects.filter(player=player).order_by("tick_number")
            for player_tick in player_ticks:
                PlayerTickDup.objects.create(tick_number=player_tick.tick_number, player=player,
                                             action=player_tick.action, is_red_security=player_tick.is_red_security,
                                             is_blue_security=player_tick.is_blue_security,
                                             is_blue_capability=player_tick.is_blue_capability,
                                             is_yellow_security=player_tick.is_yellow_security,
                                             is_yellow_capability=player_tick.is_yellow_capability,
                                             is_red_capability=player_tick.is_red_capability,
                                             is_attack=attack_dict[player_tick.tick_number],
                                             is_peer_sanction=player_tick.is_peer_sanction,
                                             is_manager_sanction=player_tick.is_manager_sanction)

# game_id_queryset = PlayerTick.objects.values_list("player__game__id", flat = True).distinct()
# game_id_list = list(game_id_queryset)
#  Game.objects.exclude(id__in = game_id_list).delete()

# defaultdict(list,
#             {2: [57, 58, 59, 60, 63, 64, 65, 66],
#              3: [30, 31, 38, 39, 40, 41, 69, 70, 71, 72],
#              4: [23, 24, 32, 34, 35, 44, 45, 46, 47],
#              5: [18, 19, 20, 21, 22]})


#
# 11
# 15
# 9
# 15
# 7
# 13
# 9
# 3
# 10
# 7
# 9
# 3
# 0
# 0
# 11
# 10
# 11
# 13
# 10
# 8
# 8
# 8
# 9
# 13
# 8
# 13
# 15
# 17
# 0
# 4
# 5
# 11
# 3
# 13

#

#
# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 117.6470588
# 47.05882353
# 40
# 20
# 0
# 20
# 12.5
# 25
# 12.5
# 0
# 100
# 25
# 50
# 0
# 16.66666667
# 50
# 50
# 60
# 20
# 60
# 0
# 0
# 72.72727273
# 0
# 0
# 0
# 90.90909091
# 18.18181818
# 0
# 0
# 44.44444444
# 0
# 0
# 16.66666667
# 0
# 13.33333333
# 85.71428571
# 0
# 0
# 62.5
# 25
# 0

#
# 100
# 100
# 100
# 100
# 100
# 44.44444444
# 44.44444444
# 44.44444444
# 44.44444444
# 44.44444444
# 18.18181818
# 18.18181818
# 18.18181818
# 18.18181818
# 18.18181818
# 44.44444444
# 44.44444444
# 44.44444444
# 25
# 25
# 25
# 61.53846154
# 61.53846154
# 61.53846154
# 61.53846154
# 66.66666667
# 66.66666667
# 66.66666667
# 66.66666667
# 60
# 60
# 60
# 13.33333333
# 13.33333333
# 13.33333333
# 100
# 100
# 100
# 100
# 71.42857143
# 71.42857143
# 71.42857143
# 71.42857143
# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 60
# 60
# 60
# 16.66666667
# 16.66666667
# 16.66666667



#
0.0531135531136
0.564705882353
0.625882352941
0.524705882353
0.0258823529412
0.225882352941
0.195970695971
0.148351648352
0.166666666667
-0.266233766234
-0.121212121212
-0.266233766234
0.0
-0.047619047619
0.0952380952381
-0.0952380952381
0.0808080808081
0.313131313131
0.17803030303
0.0265151515152
0.148148148148
0.144249512671
0.323586744639

#
# 0.105555555556
# 0.27962962963
# -0.127777777778
# 0.0
# 0.0833333333333
# 0.0
# 0.0
# 0.010582010582
# 0.0952380952381
# 0.042328042328
# 0.0
# -0.0416666666667
# -0.047619047619
# -0.0357142857143
# -0.200483091787
# -0.200483091787
# -0.0214285714286
# -0.0190476190476
# 0.109848484848
# 0.094696969697
# 0.0151515151515



#
# 540
# 470
# 530
# 495
# 435
# 270
# 225
# 270
# 190
# 160
# 385
# 270
# 405
# 415
# 315
# 190
# 315
# 360
# 375
# 370
# 335
# 380
# 315
# 305
# 340
# 460
# 450
# 450
# 430
# 385
# 280
# 450
# 405
# 450
# 345
# 450
# 440
# 410
# 405
# 405
# 350
# 400
# 315
# 370
# 340
# 495
# 450
# 315
# 360
# 355

#

# 210
# 225
# 185
# 180
# 120
# 395
# 360
# 360
# 395
# 235
# 385
# 340
# 385
# 380
# 295
# 400
# 370
# 405
# 235
# 405
# 270
# 245
# 245
# 330
# 210
# 345
# 290
# 330
# 225
# 415
# 405
# 430
# 470
# 405
# 430
# 315
# 315
# 335
# 315
# 230
# 225
# 200
# 235
# 405
# 415
# 495
# 480
# 405
# 375
# 405
# 405
# 340
# 335
# 280
# 440
# 405
# 365



#




# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 17
# 8
# 4
# 2
# 0
# 2
# 2
# 4
# 2
# 0
# 8
# 2
# 4
# 3
# 4
# 2
# 4
# 5
# 2
# 6
# 0
# 0
# 8
# 0
# 0
# 0
# 10
# 2
# 0
# 0
# 4
# 0
# 0
# 2
# 0
# 2
# 6
# 2
# 1
# 7
# 4
# 1

#
# 14
# 14
# 14
# 14
# 14
# 4
# 4
# 4
# 4
# 4
# 2
# 2
# 3
# 3
# 2
# 4
# 4
# 4
# 4
# 4
# 4
# 13
# 10
# 8
# 9
# 9
# 8
# 9
# 9
# 5
# 5
# 5
# 2
# 2
# 2
# 10
# 10
# 10
# 10
# 11
# 11
# 12
# 12
# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 0
# 6
# 6
# 6
# 2
# 2
# 2


#
2
0
0
0
1
1
1
0
1
1
1
0
1
0
1
1
1
0
0
1
1
0
1
1
2
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
2
1
1
0
2
0
0
0
0
0
2
1
2
1
1
0
1
1
2
2
0
0
0
2
1
0
0
0
0
0
2
2
1
0
2
1
0
2
1
2
0
2
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
2
1
0
0
2
2
0
0
0
0
2
1
2
0
1
1
2
0
2
0
0
1
0
3
0
1
2
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0


#
2
4
9
9
9
9
2
2
1
1
1
0
0
5
3
1
1
2
0
0
1
2
0
5
1
5
0
7
3
1
0
2
1
7
1
4
9
5
1
4
0
0
1
4
2
2
1
1
0
2
1
5
2
5
0
3
2
0
3
2
0
3
4
2
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
1
1
1
1
1
1
0
1
2
0
2
2
1
1
2
3
2
1
2
2
1
2
2
2
2
0
4
0
0
3
4
2
0
2
2
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
2
0
8
2
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0
0