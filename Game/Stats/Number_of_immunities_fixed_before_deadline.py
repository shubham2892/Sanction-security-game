from Game.models import Player, PlayerTick


def number_of_immuinities_fixed_before_deadline():
    players = Player.objects.all()
    for player in players:
        playerticks = PlayerTick.objects.filter(player = player)
        for playertick in playerticks:
            if playertick.is_attack:
                