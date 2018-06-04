from __future__ import division

from Game.models import PlayerTick, INDIVIDUAL_SANC, SECURITY_RED, SECURITY_BLUE, SECURITY_YELLOW, GROUP_SANC, Game, \
    SANCTION, PASS, PlayerTickDup, RESEARCH_TASK, ManagerSanction


def number_of_security_tasks():
    two_player_games = [57, 58, 59, 60, 63, 64, 65, 66]
    three_player_games = [30, 31, 38, 39, 40, 41, 69, 70, 71, 72]
    four_player_games = [23, 24, 32, 34, 35, 44, 45, 46, 47]
    five_player_games = [18, 19, 20, 21, 22]

    tasks_in_two_player = PlayerTickDup.objects.filter(player__game__manager_sanc=GROUP_SANC,
                                                       player__game__id__in=two_player_games,
                                                       action=RESEARCH_TASK).count()
    tasks_in_three_player = PlayerTickDup.objects.filter(player__game__manager_sanc=GROUP_SANC,
                                                         player__game__id__in=three_player_games,
                                                         action=RESEARCH_TASK).count()
    tasks_in_four_player = PlayerTickDup.objects.filter(player__game__manager_sanc=GROUP_SANC,
                                                        player__game__id__in=four_player_games,
                                                        action=RESEARCH_TASK).count()
    tasks_in_five_player = PlayerTickDup.objects.filter(player__game__manager_sanc=GROUP_SANC,
                                                        player__game__id__in=five_player_games,
                                                        action=RESEARCH_TASK).count()

    tasks_in_two_player_in = PlayerTickDup.objects.filter(player__game__manager_sanc=INDIVIDUAL_SANC,
                                                          player__game__id__in=two_player_games,
                                                          action=RESEARCH_TASK).count()
    tasks_in_three_player_in = PlayerTickDup.objects.filter(player__game__manager_sanc=INDIVIDUAL_SANC,
                                                            player__game__id__in=three_player_games,
                                                            action=RESEARCH_TASK).count()
    tasks_in_four_player_in = PlayerTickDup.objects.filter(player__game__manager_sanc=INDIVIDUAL_SANC,
                                                           player__game__id__in=four_player_games,
                                                           action=RESEARCH_TASK).count()
    tasks_in_five_player_in = PlayerTickDup.objects.filter(player__game__manager_sanc=INDIVIDUAL_SANC,
                                                           player__game__id__in=five_player_games,
                                                           action=RESEARCH_TASK).count()

    individual_sanctions_two = ManagerSanction.objects.filter(game__manager_sanc=INDIVIDUAL_SANC,
                                                              game__id__in=two_player_games).count()
    individual_sanctions_three = ManagerSanction.objects.filter(game__manager_sanc=INDIVIDUAL_SANC,
                                                                game__id__in=three_player_games, ).count()
    individual_sanctions_four = ManagerSanction.objects.filter(game__manager_sanc=INDIVIDUAL_SANC,
                                                               game__id__in=four_player_games).count()
    individual_sanctions_five = ManagerSanction.objects.filter(game__manager_sanc=INDIVIDUAL_SANC,
                                                               game__id__in=five_player_games, ).count()

    GROUP_sanctions_two = ManagerSanction.objects.filter(game__manager_sanc=GROUP_SANC,
                                                         game__id__in=two_player_games).count()
    GROUP_sanctions_three = ManagerSanction.objects.filter(game__manager_sanc=GROUP_SANC,
                                                           game__id__in=three_player_games, ).count()
    GROUP_sanctions_four = ManagerSanction.objects.filter(game__manager_sanc=GROUP_SANC,
                                                          game__id__in=four_player_games).count()
    GROUP_sanctions_five = ManagerSanction.objects.filter(game__manager_sanc=GROUP_SANC,
                                                          game__id__in=five_player_games, ).count()

    print individual_sanctions_two
    print GROUP_sanctions_two
    print individual_sanctions_two / (len(two_player_games * 2))
    print GROUP_sanctions_two / (len(two_player_games * 2))

    print "--------"
    print individual_sanctions_three
    print GROUP_sanctions_three
    print individual_sanctions_three / (len(three_player_games * 3))
    print GROUP_sanctions_three / (len(three_player_games * 3))

    print "--------"
    print individual_sanctions_four
    print GROUP_sanctions_four
    print individual_sanctions_four / (len(four_player_games * 4))
    print GROUP_sanctions_four / (len(four_player_games * 4))

    print "--------"
    print individual_sanctions_five
    print GROUP_sanctions_five
    print individual_sanctions_five / (len(four_player_games * 5))
    print GROUP_sanctions_five / (len(four_player_games * 5))

    print "--------"

    print "Tasks completed in two player game per game per player:{}".format(
        tasks_in_two_player / (len(two_player_games) * 2))
    print "Tasks completed in three player game per game per player:{}".format(
        tasks_in_three_player / (len(three_player_games) * 3))
    print "Tasks completed in four player game per game per player:{}".format(
        tasks_in_four_player / (len(four_player_games) * 4))
    print "Tasks completed in five player game per game per player:{}".format(
        tasks_in_five_player / (len(five_player_games) * 5))

    print "Tasks completed in two player game per game per player individual:{}".format(
        tasks_in_two_player_in / (len(two_player_games) * 2))
    print "Tasks completed in three player game per game per player individual:{}".format(
        tasks_in_three_player_in / (len(three_player_games) * 3))
    print "Tasks completed in four player game per game per player individual:{}".format(
        tasks_in_four_player_in / (len(four_player_games) * 4))
    print "Tasks completed in five player game per game per player individual:{}".format(
        tasks_in_five_player_in / (len(five_player_games) * 5))
