from collections import defaultdict

from django.db.models import Q

from Game.models import Player, Game, PlayerTickDup, RED, SECURITY_RED, SECURITY_YELLOW, YELLOW, BLUE, SECURITY_BLUE, \
    PlayerTickDatabase, LAB, ManagerSanction, RESEARCH_TASK, CONFERENCE_VALUE, WORKSHOP_VALUE, JOURNAL_VALUE


def number_of_immunities_fixed_before_deadline(player, game):
    number_of_immunities_fixed = 0
    number_of_red = 0
    number_of_yellow = 0
    number_of_blue = 0
    player_ticks = PlayerTickDup.objects.filter(player=player).order_by("tick_number")
    immunity_map = defaultdict(lambda: True)
    for player_tick in player_ticks:
        if player_tick.is_attack == RED:
            if PlayerTickDup.objects.get(player=player,
                                         tick_number=player_tick.tick_number).action == SECURITY_RED and immunity_map[
                player_tick.tick_number]:
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number] = False

                number_of_red += 1

            elif player_tick.tick_number + 1 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 1).action == SECURITY_RED and \
                    immunity_map[player_tick.tick_number + 1]:
                number_of_red += 1
                immunity_map[player_tick.tick_number + 1] = False

                number_of_immunities_fixed += 1
            elif player_tick.tick_number + 2 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 2).action == SECURITY_RED and \
                    immunity_map[player_tick.tick_number + 2]:
                number_of_red += 1
                immunity_map[player_tick.tick_number + 2] = False

                number_of_immunities_fixed += 1
        elif player_tick.is_attack == YELLOW:
            if PlayerTickDup.objects.get(player=player,
                                         tick_number=player_tick.tick_number).action == SECURITY_YELLOW and \
                    immunity_map[player_tick.tick_number]:
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number] = False

                number_of_yellow += 1
            elif player_tick.tick_number + 1 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 1).action == SECURITY_YELLOW and \
                    immunity_map[player_tick.tick_number + 1]:
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number + 1] = False

                number_of_yellow += 1

            elif player_tick.tick_number + 2 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 2).action == SECURITY_YELLOW and \
                    immunity_map[player_tick.tick_number + 2]:
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number + 2] = False

                number_of_yellow += 1

        elif player_tick.is_attack == BLUE:
            if PlayerTickDup.objects.get(player=player,
                                         tick_number=player_tick.tick_number).action == SECURITY_BLUE and immunity_map[
                player_tick.tick_number]:
                number_of_immunities_fixed += 1
                number_of_blue += 1
                immunity_map[player_tick.tick_number] = False
            elif player_tick.tick_number + 1 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 1).action == SECURITY_BLUE and \
                    immunity_map[player_tick.tick_number + 1]:
                number_of_immunities_fixed += 1
                number_of_blue += 1
                immunity_map[player_tick.tick_number + 1] = False
            elif player_tick.tick_number + 2 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 2).action == SECURITY_BLUE and \
                    immunity_map[player_tick.tick_number + 2]:
                number_of_immunities_fixed += 1
                number_of_blue += 1
                immunity_map[player_tick.tick_number + 2] = False
        elif player_tick.is_attack == LAB:
            if PlayerTickDup.objects.get(player=player,
                                         tick_number=player_tick.tick_number).action == SECURITY_BLUE and immunity_map[
                player_tick.tick_number]:
                number_of_immunities_fixed += 1
                number_of_blue += 1
                immunity_map[player_tick.tick_number] = False
            elif player_tick.tick_number + 1 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 1).action == SECURITY_BLUE and \
                    immunity_map[player_tick.tick_number + 1]:
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number + 1] = False
                number_of_blue += 1
            elif player_tick.tick_number + 2 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 2).action == SECURITY_BLUE and \
                    immunity_map[player_tick.tick_number + 2]:
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number + 2] = False
                number_of_blue += 1

            if PlayerTickDup.objects.get(player=player,
                                         tick_number=player_tick.tick_number).action == SECURITY_YELLOW and \
                    immunity_map[player_tick.tick_number]:
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number] = False

                number_of_yellow += 1

            elif player_tick.tick_number + 1 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 1).action == SECURITY_YELLOW and \
                    immunity_map[player_tick.tick_number + 1]:
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number + 1] = False

                number_of_yellow += 1

            elif player_tick.tick_number + 2 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 2).action == SECURITY_YELLOW and \
                    immunity_map[player_tick.tick_number + 2]:
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number + 2] = False

                number_of_yellow += 1

            if PlayerTickDup.objects.get(player=player,
                                         tick_number=player_tick.tick_number).action == SECURITY_RED and immunity_map[
                player_tick.tick_number]:
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number] = False

                number_of_red += 1

            elif player_tick.tick_number + 1 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 1).action == SECURITY_RED and \
                    immunity_map[player_tick.tick_number + 1]:
                number_of_red += 1
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number + 1] = False

            elif player_tick.tick_number + 2 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 2).action == SECURITY_RED and \
                    immunity_map[player_tick.tick_number + 2]:
                number_of_red += 1
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number + 2] = False

    # print "=============number of immunities before deadline {}========================".format(player.id)
    # print number_of_red
    # print number_of_yellow
    # print number_of_blue
    return number_of_immunities_fixed


def number_immunities_fixed(player, game):
    red_security_tasks_individual = PlayerTickDup.objects.filter(player=player,
                                                                 action=SECURITY_RED).count()
    blue_security_tasks_individual = PlayerTickDup.objects.filter(player=player,
                                                                  action=SECURITY_BLUE).count()
    yellow_security_tasks_individual = PlayerTickDup.objects.filter(player=player,
                                                                    action=SECURITY_YELLOW).count()
    # print "=============number of immunities {}========================".format(player.id)
    # print red_security_tasks_individual
    # print yellow_security_tasks_individual
    # print blue_security_tasks_individual
    return red_security_tasks_individual + blue_security_tasks_individual + yellow_security_tasks_individual


def number_of_manager_sanction(player, game):
    number_of_manager_sanction = ManagerSanction.objects.filter(sanctionee=player).count()
    return number_of_manager_sanction


def number_of_tasks_completed(player, game):
    number_of_tasks_completed = PlayerTickDup.objects.filter(player=player, action=RESEARCH_TASK).count()
    return number_of_tasks_completed


def score_player(player, game):
    return player.nf_conference * CONFERENCE_VALUE + player.nf_workshop * WORKSHOP_VALUE + player.nf_journal * JOURNAL_VALUE


def number_of_attacks(player, game):
    return PlayerTickDup.objects.filter(player=player, is_attack__gt=0).count()


def number_ticks_to_fix_capability(player, game):
    no_of_ticks_taken = 0

    player_ticks = PlayerTickDup.objects.filter(player=player, action=SECURITY_RED)
    for player_tick in player_ticks:
        if player_tick.is_red_capability:
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player, tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == RED:
                    # no_of_ticks_taken += i
                    break
        else:
            count_attack = 0
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player, tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == RED:
                    if count_attack == 0:
                        count_attack += 1
                    else:
                        no_of_ticks_taken += i
                        break

    player_ticks = PlayerTickDup.objects.filter(player=player, action=SECURITY_BLUE)
    for player_tick in player_ticks:
        if player_tick.is_blue_capability:
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player,
                                                                 tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == BLUE:
                    # no_of_ticks_taken += i
                    break
        else:
            count_attack = 0
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player,
                                                                 tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == BLUE:
                    if count_attack == 0:
                        count_attack += 1
                    else:
                        no_of_ticks_taken += i
                        break

    player_ticks = PlayerTickDup.objects.filter(player=player, action=SECURITY_YELLOW)
    for player_tick in player_ticks:
        if player_tick.is_yellow_capability:
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player,
                                                                 tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == YELLOW:
                    # no_of_ticks_taken += i
                    break
        else:
            count_attack = 0
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player,
                                                                 tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == YELLOW:
                    if count_attack == 0:
                        count_attack += 1
                    else:
                        no_of_ticks_taken += i
                        break

    return no_of_ticks_taken


def number_ticks_to_fix_immunity(player, game):
    no_of_ticks_taken = 0

    player_ticks = PlayerTickDup.objects.filter(player=player, action=SECURITY_RED)
    for player_tick in player_ticks:
        if player_tick.is_red_capability:
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player, tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == RED:
                    no_of_ticks_taken += i
                    break
        else:
            count_attack = 0
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player, tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == RED:
                    if count_attack == 0:
                        count_attack += 1
                    else:
                        no_of_ticks_taken += i
                        break

    player_ticks = PlayerTickDup.objects.filter(player=player, action=SECURITY_BLUE)
    for player_tick in player_ticks:
        if player_tick.is_blue_capability:
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player,
                                                                 tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == BLUE:
                    no_of_ticks_taken += i
                    break
        else:
            count_attack = 0
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player,
                                                                 tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == BLUE:
                    if count_attack == 0:
                        count_attack += 1
                    else:
                        no_of_ticks_taken += i
                        break

    player_ticks = PlayerTickDup.objects.filter(player=player, action=SECURITY_YELLOW)
    for player_tick in player_ticks:
        if player_tick.is_yellow_capability:
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player,
                                                                 tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == YELLOW:
                    no_of_ticks_taken += i
                    break
        else:
            count_attack = 0
            for i in range(0, 6):
                player_tick_dup_temp = PlayerTickDup.objects.get(player=player,
                                                                 tick_number=player_tick.tick_number - i)
                if player_tick_dup_temp.is_attack == LAB or player_tick_dup_temp.is_attack == YELLOW:
                    if count_attack == 0:
                        count_attack += 1
                    else:
                        no_of_ticks_taken += i
                        break

    return no_of_ticks_taken


def player_game_wise_stats():
    games = Game.objects.all()
    for game in games:
        players = Player.objects.filter(game=game)
        for player in players:
            no_of_immunities_fixed_before_deadline = number_of_immunities_fixed_before_deadline(player, game)
            no_of_immunities_fixed = number_immunities_fixed(player, game)
            no_of_manager_sanction = number_of_manager_sanction(player, game)
            no_of_tasks_completed = number_of_tasks_completed(player, game)
            # no_ticks_taken_to_complete_immunity_tasks = no_ticks_to_fix_immunity(player, game)
            no_of_attacks = number_of_attacks(player, game)

            PlayerTickDatabase.objects.create(player_username=player.user.username, game_key=game.game_key,
                                              game_type=game.manager_sanc,
                                              number_of_manager_sanctions=no_of_manager_sanction,
                                              number_of_immunities_fixed=no_of_immunities_fixed,
                                              number_of_tasks_completed=no_of_tasks_completed,
                                              number_of_attacks=no_of_attacks,
                                              player_score=score_player(player, game),
                                              time_to_fix_immunity=number_ticks_to_fix_immunity(player, game),
                                              time_to_fix_capability=number_ticks_to_fix_capability(player, game),
                                              number_immnunities_fixed_before_deadline=no_of_immunities_fixed_before_deadline)
