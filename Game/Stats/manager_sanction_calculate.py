from Game.models import ManagerSanction, INDIVIDUAL_SANC, GROUP_SANC, Game


def calculate_manager_sanctions():
    individual_sanctions_unique_ticks = ManagerSanction.objects.filter(game__manager_sanc=INDIVIDUAL_SANC).values(
        "tick_number").distinct().count()
    group_sanctions_unique_ticks = ManagerSanction.objects.filter(game__manager_sanc=GROUP_SANC).values(
        "tick_number").distinct().count()
    individual_sanctions = ManagerSanction.objects.filter(game__manager_sanc=INDIVIDUAL_SANC).count()
    group_sanctions = ManagerSanction.objects.filter(game__manager_sanc=GROUP_SANC).count()

    individual_sanction_game = Game.objects.filter(manager_sanc=INDIVIDUAL_SANC).count()
    group_sanction_game = Game.objects.filter(manager_sanc=GROUP_SANC).count()
    print "\item No. of games of individual sanctions:{}".format(individual_sanction_game)
    print "\item No. of games of group sanctions:{}".format(group_sanction_game)
    print "\item No. of individual sanctions unique ticks:{}".format(individual_sanctions_unique_ticks)
    print "\item No. of group sanctions unique ticks:{}".format(group_sanctions_unique_ticks)
    print "\item No. of sanctions per individual sanction game(unique ticks):{}".format(
        individual_sanctions_unique_ticks / individual_sanction_game)
    print "\item No. of sanctions per group sanction game(unique ticks):{}".format(
        group_sanctions_unique_ticks / group_sanction_game)

    print "\item No. of individual sanctions:{}".format(individual_sanctions)
    print "\item No. of group sanctions:{}".format(group_sanctions)
    print "\item No. of sanctions per individual sanction game:{}".format(
        individual_sanctions / individual_sanction_game)
    print "\item No. of sanctions per group sanction game:{}".format(group_sanctions / group_sanction_game)


if __name__ == "__main__":
    calculate_manager_sanctions()
