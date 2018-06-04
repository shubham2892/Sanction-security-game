from __future__ import division

from Game.models import PlayerTick, INDIVIDUAL_SANC, SECURITY_RED, SECURITY_BLUE, SECURITY_YELLOW, GROUP_SANC, Game, \
    SANCTION, PASS, Message


def number_of_times_sanctions_occur():
    group_sanction_messages = Message.objects.filter(tick__game__manager_sanc=GROUP_SANC)
    group_sanctions = 0
    individual_sanction_game = Game.objects.filter(manager_sanc=INDIVIDUAL_SANC).count()
    group_sanction_game = Game.objects.filter(manager_sanc=GROUP_SANC).count()
    for message in group_sanction_messages:
        message_list = message.content.split()
        if message_list[2] == "Group" and message_list[3] == "Sanctioned":
            group_sanctions += 1

    individual_sanction_message = Message.objects.filter(tick__game__manager_sanc=INDIVIDUAL_SANC)
    individual_sanctions = 0
    for message in individual_sanction_message:
        message_list = message.content.split()
        if message_list[2] == "Sanctioned" and message_list[3] == "for":
            individual_sanctions += 1

    print "No of individual sanctions per game:{}".format(individual_sanctions / individual_sanction_game)
    print "No of group sanctions per game:{}".format(group_sanctions / group_sanction_game)


def number_of_security_tasks():
    red_security_tasks_individual = PlayerTick.objects.filter(player__game__manager_sanc=INDIVIDUAL_SANC,
                                                              action=SECURITY_RED).count()
    blue_security_tasks_individual = PlayerTick.objects.filter(player__game__manager_sanc=INDIVIDUAL_SANC,
                                                               action=SECURITY_BLUE).count()
    yellow_security_tasks_individual = PlayerTick.objects.filter(player__game__manager_sanc=INDIVIDUAL_SANC,
                                                                 action=SECURITY_YELLOW).count()

    red_security_tasks_group = PlayerTick.objects.filter(player__game__manager_sanc=GROUP_SANC,
                                                         action=SECURITY_RED).count()
    blue_security_tasks_group = PlayerTick.objects.filter(player__game__manager_sanc=GROUP_SANC,
                                                          action=SECURITY_BLUE).count()
    yellow_security_tasks_group = PlayerTick.objects.filter(player__game__manager_sanc=GROUP_SANC,
                                                            action=SECURITY_YELLOW).count()

    peer_sanction_individual = PlayerTick.objects.filter(player__game__manager_sanc=INDIVIDUAL_SANC,
                                                         action=SANCTION).count()

    peer_sanction_group = PlayerTick.objects.filter(player__game__manager_sanc=GROUP_SANC, action=SANCTION).count()

    individual_sanction_game = Game.objects.filter(manager_sanc=INDIVIDUAL_SANC).count()
    group_sanction_game = Game.objects.filter(manager_sanc=GROUP_SANC).count()

    ticks_wasted_in_pass_individual = PlayerTick.objects.filter(player__game__manager_sanc=INDIVIDUAL_SANC,
                                                                action=PASS).count()

    ticks_wasted_in_pass_group = PlayerTick.objects.filter(player__game__manager_sanc=GROUP_SANC,
                                                           action=PASS).count()

    print red_security_tasks_individual
    print yellow_security_tasks_individual
    print blue_security_tasks_individual

    print red_security_tasks_group
    print yellow_security_tasks_group
    print blue_security_tasks_group

    print "No. of games of individual sanctions:{}".format(individual_sanction_game)
    print "No. of games of group sanctions:{}".format(group_sanction_game)

    print "No. of security tasks fixed in individual sanction game:{}".format(
        red_security_tasks_individual + blue_security_tasks_individual + yellow_security_tasks_individual)
    print "No. of security tasks fixed in group sanction game:{}".format(
        red_security_tasks_group + yellow_security_tasks_group + blue_security_tasks_group)
    print "No. of security tasks fixed per individual sanction game:{}".format((
                                                                                       red_security_tasks_individual + blue_security_tasks_individual + yellow_security_tasks_individual) / individual_sanction_game)

    print "No. of security tasks fixed per group sanction game:{}".format(
        (red_security_tasks_group + yellow_security_tasks_group + blue_security_tasks_group) / group_sanction_game)

    print "No. of peer sanction in individual sanction:{}".format(peer_sanction_individual)
    print "No. of peer sanction in group sanction:{}".format(peer_sanction_group)

    print "No. of peer sanction in individual sanction per game:{}".format(
        float(peer_sanction_individual / individual_sanction_game))
    print "No. of peer sanction in group sanction per game:{}".format(float(peer_sanction_group / group_sanction_game))

    print ("No. of ticks wasted in PASS in individual sanction:{}").format(ticks_wasted_in_pass_individual)
    print ("No. of ticks wasted in PASS in group sanction:{}").format(ticks_wasted_in_pass_group)

    print ("No. of ticks wasted in PASS in individual sanction per game:{}").format(
        ticks_wasted_in_pass_individual / individual_sanction_game)
    print ("No. of ticks wasted in PASS in group sanction per game:{}").format(
        ticks_wasted_in_pass_group / group_sanction_game)
