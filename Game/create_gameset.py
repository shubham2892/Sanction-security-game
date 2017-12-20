from django.contrib.auth.models import User

from Game.models import Game, INDIVIDUAL_SANC, GROUP_SANC, Player, GameSet


def create_game_set(player_ids):
    TOTAL_TICKS = 35
    ATTACK_FREQUENCY = 30
    game_1_demo = Game.objects.create(total_ticks=25, manager_sanc=INDIVIDUAL_SANC, attack_frequency=40)
    game_2_demo = Game.objects.create(total_ticks=25, manager_sanc=GROUP_SANC, attack_frequency=40)
    game_1 = Game.objects.create(total_ticks=TOTAL_TICKS, manager_sanc=INDIVIDUAL_SANC,
                                 attack_frequency=ATTACK_FREQUENCY)
    game_2 = Game.objects.create(total_ticks=TOTAL_TICKS, manager_sanc=INDIVIDUAL_SANC,
                                 attack_frequency=ATTACK_FREQUENCY)
    game_3 = Game.objects.create(total_ticks=TOTAL_TICKS, manager_sanc=GROUP_SANC, attack_frequency=ATTACK_FREQUENCY)
    game_4 = Game.objects.create(total_ticks=TOTAL_TICKS, manager_sanc=GROUP_SANC, attack_frequency=ATTACK_FREQUENCY)

    for player_id in player_ids:
        user = User.objects.create_user(player_id, password=player_id)
        player_demo_1 = Player.objects.create(user=user, game=game_1_demo)
        player_demo_2 = Player.objects.create(user=user, game=game_2_demo)
        player_1 = Player.objects.create(user=user, game=game_1)
        player_2 = Player.objects.create(user=user, game=game_2)
        player_3 = Player.objects.create(user=user, game=game_3)
        player_4 = Player.objects.create(user=user, game=game_4)

        GameSet.objects.create(user=user, demo_game_1=game_1_demo, demo_game_2=game_2_demo,
                               game_1=game_1, game_2=game_2, game_3=game_3, game_4=game_4)
