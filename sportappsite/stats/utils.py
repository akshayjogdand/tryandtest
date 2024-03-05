def get_player_performance(player, match, performance_klass):
    try:
        return performance_klass.objects.get(player=player, match=match)
    except performance_klass.DoesNotExist:
        pass
