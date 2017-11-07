from Game.models import Game, Player, PlayerTick


def pertick_player_data():
    player_tick_data = {}
    games = Game.objects.all()
    for game in games:
        players = Player.objects.filter(game=game)
        for player in players:
            player_ticks = PlayerTick.objects.filter(player=player)
            for player_tick in player_ticks:
                red_immunity = True
                red_capability = True
                is_attack = True
                is_manager_sanction = True
                is_peer_sanction = True

                dict_obj = {}
                dict_obj["player_username"] = player.user.username
                dict_obj["tick_number"] = player_tick.tick_number
                dict_obj["game_id"] = game.game_key
