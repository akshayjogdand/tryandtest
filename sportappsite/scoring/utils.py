from stats.models import PlayerScores

from stats.scoring import score_performances


def get_player_scores(player, match):
    try:
        scores = PlayerScores.objects.get(player=player, match=match)
    except PlayerScores.DoesNotExist:
        return
    else:
        return scores


def score(player, match, scores):
    total = 0.00

    for result in score_performances(player, match):
        result.save()
        total = total + float(result.result)
        scores.detailed_scoring.add(result)
        scores.total_score = total

    return scores


def get_or_score_player_performance(player, match, re_score):
    scores = get_player_scores(player, match)

    if not scores:
        scores = PlayerScores()
        scores.player = player
        scores.match = match
        scores.team = player.team(match)
        scores.save()
        score(player, match, scores)

    else:
        if re_score:
            scores.total_score = 0.00
            for r in scores.detailed_scoring.all():
                r.delete()
            score(player, match, scores)

    scores.save()
    return scores


def get_or_score_match_player_performances(match, re_score):
    squads = [match.team_one, match.team_two]
    match_scores = {}

    for squad in squads:
        for player in squad.players.all():
            match_scores[player] = get_or_score_player_performance(
                player, match, re_score
            )

    return match_scores


def rule_results_as_table(results):
    table = """<table frame='border' rules='all'>
            <tr>
             <th>Name</th>
             <th>Input</th>
             <th>Calculation</th>
             <th>Points/Factor</th>
             <th>Result</th>
            </tr> """

    for r in results:
        row = (
            "<tr> "
            "<td>{}</td>"
            "<td>{}</td>"
            "<td>{}</td>"
            "<td>{}</td>"
            "<td>{}</td>"
            " </tr>"
        ).format(r, r.input_values, r.calculation, r.points_or_factor, r.result)

        table = table + row

    table = table + "</table>"
    return table
