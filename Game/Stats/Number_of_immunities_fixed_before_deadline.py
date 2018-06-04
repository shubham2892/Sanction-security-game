import csv
import os
from collections import defaultdict

from django.contrib.auth.models import User
from django.db.models import Sum

from Game.models import Player, Game, PlayerTickDup, RED, SECURITY_RED, SECURITY_YELLOW, YELLOW, BLUE, SECURITY_BLUE, \
    PlayerTickDatabase, LAB, ManagerSanction, RESEARCH_TASK, CONFERENCE_VALUE, WORKSHOP_VALUE, JOURNAL_VALUE, PASS


def get_group_dospert_score():
    games = Game.objects.filter(manager_sanc=1)
    immunities_score = []
    dosper_score_dict = dospert_scale_analysis("Presurvey-mturk.csv")

    for game in games:
        playertickdatabase = PlayerTickDatabase.objects.filter(game_type=1, game_key=game.game_key)
        dospert_score = 0
        number_of_immunities_fixed = 0
        count = playertickdatabase.count()
        for player in playertickdatabase:
            # print dosper_score_dict[player.player_username]['social']
            # print player.number_of_immunities_fixed
            dospert_score += dosper_score_dict[player.player_username]['social']
            number_of_immunities_fixed += player.number_of_immunities_fixed

        # print count
        # print dospert_score
        immunities_score.append(
            {"dospert_score": get_range_dospert(dospert_score / count),
             "immunities_fixed": (number_of_immunities_fixed / count)})

    print immunities_score


def calculate_individual_attacks():
    players = Player.objects.all()
    player_attack_dictionary = {}
    player_total_attacks = []
    for player in players:
        playertickdups = PlayerTickDup.objects.filter(player=player)
        red_count = 0
        yellow_count = 0
        blue_count = 0
        lab_count = 0

        for playertickdup in playertickdups:
            if playertickdup.is_attack == RED:
                red_count += 1
            elif playertickdup.is_attack == YELLOW:
                yellow_count += 1
            elif playertickdup.is_attack == BLUE:
                blue_count += 1
            else:
                lab_count += 1
        player_attack_dictionary[player.id] = {"red": red_count, "blue": blue_count, "yellow": yellow_count, "lab": LAB}
        player_total_attacks.append(red_count + blue_count + yellow_count + lab_count * 3)
    return player_total_attacks


def side_by_side_data():
    users = User.objects.all()
    differences_sum = 0
    difference_array = []
    first_game_array = []
    second_game_array = []
    player_attack_dictionary = calculate_individual_attacks()
    for user in users:
        playertickdatabase = PlayerTickDatabase.objects.filter(player_username=user.username).order_by(
            "game_key")
        if playertickdatabase.count() == 4:
            playertickdatabase_indi = PlayerTickDatabase.objects.filter(game_type=1,
                                                                        player_username=user.username).order_by(
                "game_key")
            playertickdatabase_group = PlayerTickDatabase.objects.filter(game_type=2,
                                                                         player_username=user.username).order_by(
                "game_key")
            first_game_array.append(playertickdatabase_indi[0].number_immnunities_fixed_before_deadline)
            first_game_array.append(playertickdatabase_indi[1].number_immnunities_fixed_before_deadline)
            second_game_array.append(playertickdatabase_group[0].number_immnunities_fixed_before_deadline)
            second_game_array.append(playertickdatabase_group[1].number_immnunities_fixed_before_deadline)

    # print len(first_game_array)
    # print len(second_game_array)
    # print print_length_wise(first_game_array)
    # print print_length_wise(second_game_array)
    print print_string(first_game_array)
    print "-------"
    print print_string(second_game_array)

def difference_between_first_second_game():
    users = User.objects.all()
    differences_sum = 0
    difference_array = []
    player_attack_dictionary = calculate_individual_attacks()
    for user in users:
        playertickdatabase = PlayerTickDatabase.objects.filter(game_type=1, player_username=user.username).order_by(
            "game_key")

        if playertickdatabase.count() == 2:
            player_id_one = Player.objects.get(game__game_key=playertickdatabase[0].game_key,
                                               user__username=playertickdatabase[0].player_username).id
            player_id_two = Player.objects.get(game__game_key=playertickdatabase[1].game_key,
                                               user__username=playertickdatabase[1].player_username).id
            # print player_id_two
            total_attack_two = player_attack_dictionary[player_id_two]["red"] + \
                               player_attack_dictionary[player_id_two]["blue"] + \
                               player_attack_dictionary[player_id_two]["yellow"] + 3 * \
                               player_attack_dictionary[player_id_two]["lab"]

            total_attack_one = player_attack_dictionary[player_id_one]["red"] + \
                               player_attack_dictionary[player_id_one]["blue"] + \
                               player_attack_dictionary[player_id_one]["yellow"] + 3 * \
                               player_attack_dictionary[player_id_one]["lab"]

            temp = (playertickdatabase[1].number_immnunities_fixed_before_deadline * 1.0 / total_attack_two -
                    playertickdatabase[
                        0].number_immnunities_fixed_before_deadline * 1.0 / total_attack_one)
            print "-----------------------"
            print playertickdatabase[1].number_immnunities_fixed_before_deadline * 1.0 / total_attack_two
            print playertickdatabase[0].number_immnunities_fixed_before_deadline * 1.0 / total_attack_one
            print "-----------------------"
            differences_sum += temp
            difference_array.append(temp)

    # print differences_sum
    # print difference_array
    print_string(difference_array)
    print_length_wise(difference_array)


def print_length_wise(input_array):
    for diff in input_array:
        print diff


def print_string(input_array):
    string_print = ""
    for diff in input_array:
        string_print += "{}\\\\ ".format(diff)
    print string_print


def player_low_high_metrics():
    player_tick_database = PlayerTickDatabase.objects.filter().all()
    dosper_score_dict = dospert_scale_analysis("Presurvey-mturk.csv")
    low_social, high_social, medium_social = 0, 0, 0
    low_players, high_players, medium_players = 0, 0, 0
    for player_tick in player_tick_database:

        mturk_id = player_tick.player_username
        dospert_score = dosper_score_dict[mturk_id]
        print dospert_score['social']
        print player_tick.number_of_manager_sanctions
        if dospert_score['social'] == 'high':
            high_social += player_tick.number_of_manager_sanctions
            high_players += 1
        elif dospert_score['social'] == 'medium':
            medium_social += player_tick.number_of_manager_sanctions
            medium_players += 1
        elif dospert_score['social'] == 'low':
            low_social += player_tick.number_of_manager_sanctions
            low_players += 1

    high_low_dict = {'low': low_social, 'medium': medium_social, 'high': high_social}
    print high_players, medium_players, low_players
    print high_low_dict


def player_total_dospert():
    dosper_score_dict = dospert_scale_analysis("Presurvey-mturk.csv")
    player_tick_query = PlayerTickDatabase.objects.filter(game_type=2).values("player_username").annotate(
        manager_sanction_sum=Sum("number_immnunities_fixed_before_deadline")).order_by("manager_sanction_sum")
    dospert_manager_dict = defaultdict()
    dospert_list = []
    sum_list = []
    for player_entry in player_tick_query:
        # print player_entry
        # print player_entry['player_username']
        dospert_manager_dict[player_entry['player_username']] = {
            "dospert": dosper_score_dict[player_entry['player_username']]['total'],
            "manager_sanctions": player_entry['manager_sanction_sum']}
        dospert_list.append(dosper_score_dict[player_entry['player_username']]['social'])
        sum_list.append(player_entry['manager_sanction_sum'])
    print dospert_manager_dict
    print "-----------------"
    print dospert_list
    print "-----------------"
    print sum_list


def dospert_scale_analysis(file_name):
    dospert_scale_dict = {}
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    c = open(os.path.join(workpath, file_name), 'rb')

    with c as csvfile:

        file_reader = csv.reader(csvfile)
        file_reader.next()
        for row in file_reader:
            for i in range(1, 31):
                row[i] = int(row[i])

            mturk_id = row[31]
            # IPIP 37 -- 56
            base_start = 0
            ethical = row[base_start + 6] + (row[base_start + 9]) + (row[base_start + 10]) + (
                row[base_start + 16]) + row[base_start + 29] + row[base_start + 30]
            Financial = row[base_start + 3] + (row[base_start + 4]) + (row[base_start + 8]) + (
                row[base_start + 12]) + row[base_start + 14] + row[base_start + 18]
            heath_safety = row[base_start + 5] + (row[base_start + 15]) + (row[base_start + 17]) + (
                row[base_start + 20]) + row[base_start + 23] + row[base_start + 26]
            recreational = row[base_start + 2] + (row[base_start + 11]) + (row[base_start + 13]) + (
                row[base_start + 19]) + row[base_start + 24] + row[base_start + 25]

            social = row[base_start + 1] + (row[base_start + 7]) + (row[base_start + 21]) + (
                row[base_start + 22]) + row[base_start + 27] + row[base_start + 28]

            # dospert_scale_dict[mturk_id] = {"ethical": ethical,
            #                                 "Financial": Financial,
            #                                 "heath_safety": heath_safety,
            #                                 "recreational": recreational,
            #                                 "social": social,
            #                                 "total": (ethical + Financial + heath_safety + recreational + social)}
            dospert_scale_dict[mturk_id] = {"ethical": get_range_dospert(ethical),
                                            "Financial": get_range_dospert(Financial),
                                            "heath_safety": get_range_dospert(heath_safety),
                                            "recreational": get_range_dospert(recreational),
                                            "social": get_range_dospert(social),
                                            "total": (ethical + Financial + heath_safety + recreational + social)}
        # print(dospert_scale_dict)
    return dospert_scale_dict


def get_range_dospert(score):
    if score <= 18:
        return "low"
    elif score >= 30:
        return "high"
    else:
        return "medium"


def number_of_immunities_fixed_before_deadline(player, game):
    number_of_immunities_fixed = 0
    number_of_red = 0
    number_of_yellow = 0
    number_of_blue = 0
    player_ticks = PlayerTickDup.objects.filter(player=player).order_by("tick_number")
    immunity_map = defaultdict(lambda: True)
    number_of_immunities_available = 0
    for player_tick in player_ticks:
        if player_tick.is_attack == RED:
            if PlayerTickDup.objects.get(player=player,
                                         tick_number=player_tick.tick_number).action == SECURITY_RED and immunity_map[
                player_tick.tick_number]:
                # print "Red Attack at {} and fixed at {}".format(player_tick.tick_number, player_tick.tick_number)
                number_of_immunities_fixed += 1
                immunity_map[player_tick.tick_number] = False

                number_of_red += 1

            elif player_tick.tick_number + 1 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 1).action == SECURITY_RED and \
                    immunity_map[player_tick.tick_number + 1]:
                # print "Red Attack at {} and fixed at {}".format(player_tick.tick_number, player_tick.tick_number + 1)

                number_of_red += 1
                immunity_map[player_tick.tick_number + 1] = False

                number_of_immunities_fixed += 1
            elif player_tick.tick_number + 2 <= 40 and PlayerTickDup.objects.get(player=player,
                                                                                 tick_number=player_tick.tick_number + 2).action == SECURITY_RED and \
                    immunity_map[player_tick.tick_number + 2]:
                # print "Red Attack at {} and fixed at {}".format(player_tick.tick_number, player_tick.tick_number + 1)

                number_of_red += 1
                immunity_map[player_tick.tick_number + 2] = False

                number_of_immunities_fixed += 1
            number_of_immunities_available += 1
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
            number_of_immunities_available += 1

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
            number_of_immunities_available += 1

        elif player_tick.is_attack == LAB:
            number_of_immunities_available += 3

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
    return number_of_immunities_fixed, number_of_immunities_available


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


def get_resilience(game_type):
    player_tick_data = PlayerTickDup.objects.filter(player__game__manager_sanc=game_type)
    round_number_list = []
    is_sanctioned_count = 0
    for player_tick in player_tick_data:
        if player_tick.is_red_security == 1:
            if is_sanctioned_count > 0 and is_sanctioned_count < 10:
                round_number_list.append(is_sanctioned_count)
                is_sanctioned_count = 0

            if player_tick.is_attack == RED or player_tick.is_attack == LAB:
                round_number_list.append(0)
        elif player_tick.is_red_security == 0:
            is_sanctioned_count += 1

    is_sanctioned_count = 0
    for player_tick in player_tick_data:
        if player_tick.is_blue_security == 1:
            if is_sanctioned_count > 0 and is_sanctioned_count < 10:
                round_number_list.append(is_sanctioned_count)
                is_sanctioned_count = 0

            if player_tick.is_attack == BLUE or player_tick.is_attack == LAB:
                round_number_list.append(0)
        elif player_tick.is_blue_security == 0:
            is_sanctioned_count += 1

    is_sanctioned_count = 0
    for player_tick in player_tick_data:
        if player_tick.is_yellow_security == 1:
            if 0 < is_sanctioned_count < 10:
                round_number_list.append(is_sanctioned_count)
                is_sanctioned_count = 0

            if player_tick.is_attack == YELLOW or player_tick.is_attack == LAB:
                round_number_list.append(0)
        elif player_tick.is_yellow_security == 0:
            is_sanctioned_count += 1
    return round_number_list


def player_game_wise_stats():
    games = Game.objects.all()
    passed_individual = []
    passed_group = []
    for game in games:
        players = Player.objects.filter(game=game)
        for player in players:
            no_of_immunities_fixed_before_deadline, number_of_immunities_available = number_of_immunities_fixed_before_deadline(
                player, game)
            no_of_immunities_fixed = number_immunities_fixed(player, game)
            no_of_manager_sanction = number_of_manager_sanction(player, game)
            no_of_tasks_completed = number_of_tasks_completed(player, game)
            # no_ticks_taken_to_complete_immunity_tasks = no_ticks_to_fix_immunity(player, game)
            dosper_score_dict = dospert_scale_analysis("Presurvey-mturk.csv")
            dosper_score = dosper_score_dict[player.user.username]["total"]
            # "ethical": ethical,
            # "Financial": Financial,
            # "heath_safety": heath_safety,
            # "recreational": recreational,
            # "social": social,
            dospert_score_ethical = dosper_score_dict[player.user.username]['ethical']
            dospert_score_social = dosper_score_dict[player.user.username]['social']
            dospert_score_financial = dosper_score_dict[player.user.username]['Financial']
            dospert_score_recreational = dosper_score_dict[player.user.username]['recreational']
            dospert_score_health_safety = dosper_score_dict[player.user.username]['heath_safety']

            no_of_attacks = number_of_attacks(player, game)
            if game.manager_sanc == 1:
                passed_individual.append(PlayerTickDup.objects.filter(player=player, action=PASS).count())
            else:
                passed_group.append(PlayerTickDup.objects.filter(player=player, action=PASS).count())

            PlayerTickDatabase.objects.create(player_username=player.user.username, game_key=game.game_key,
                                              game_type=game.manager_sanc,
                                              number_of_immunities_available=number_of_immunities_available,
                                              number_of_manager_sanctions=no_of_manager_sanction,
                                              number_of_immunities_fixed=no_of_immunities_fixed,
                                              number_of_tasks_completed=no_of_tasks_completed,
                                              number_of_attacks=no_of_attacks,
                                              player_score=score_player(player, game),
                                              time_to_fix_immunity=number_ticks_to_fix_immunity(player, game),
                                              time_to_fix_capability=number_ticks_to_fix_capability(player, game),
                                              dospert_score=dosper_score,
                                              dospert_score_ethical=dospert_score_ethical,
                                              dospert_score_social=dospert_score_social,
                                              dospert_score_financial=dospert_score_financial,
                                              dospert_score_recreational=dospert_score_recreational,
                                              dospert_score_health_safety=dospert_score_health_safety,
                                              number_immnunities_fixed_before_deadline=no_of_immunities_fixed_before_deadline)

    print passed_individual

    print passed_group