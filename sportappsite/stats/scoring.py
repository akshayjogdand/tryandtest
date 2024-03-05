from rules.models import PlayerScoringMethod, PlayerScoringResult

from .models import (
    BattingPerformance,
    BowlingPerformance,
    FieldingPerformance,
    MatchPerformance,
)

from scoring.scoring import run_rule

RULE_INPUT_VARIABLES = {
    BattingPerformance: "batting_performance",
    BowlingPerformance: "bowling_performance",
    FieldingPerformance: "fielding_performance",
    MatchPerformance: "player_match_stats",
}


def score_player_batting(player, match):
    return score_player_performance(
        player,
        match,
        BattingPerformance,
        PlayerScoringMethod.apply_on_batting_performance,
    )


def score_player_bowling(player, match):
    return score_player_performance(
        player,
        match,
        BowlingPerformance,
        PlayerScoringMethod.apply_on_bowling_performance,
    )


def score_player_fielding(player, match):
    return score_player_performance(
        player,
        match,
        FieldingPerformance,
        PlayerScoringMethod.apply_on_fielding_performance,
    )


def score_player_match_performance(player, match):
    return score_player_performance(
        player, match, MatchPerformance, PlayerScoringMethod.apply_on_match_performance
    )


def score_performances(player, match):
    return (
        score_player_batting(player, match)
        + score_player_bowling(player, match)
        + score_player_fielding(player, match)
        + score_player_match_performance(player, match)
    )


def score_player_performance(
    player, match, performance_type_klass, rule_performance_discriminator
):
    results = []
    dynamic_restriction = {
        rule_performance_discriminator.field.attname: True,
        "is_enabled": True,
    }

    try:

        if not performance_type_klass.objects.filter(
            match=match, player=player
        ).exists():
            print(
                "\t\tNo {} found for {}".format(
                    performance_type_klass.__name__, player.name
                )
            )
            return results

        player_performances = performance_type_klass.objects.filter(
            match=match, player=player
        )

        scoring_methods = PlayerScoringMethod.objects.filter(
            is_enabled=True, is_default=True, apply_to_match_type=match.match_type,
        ).filter(**dynamic_restriction)

        for performance in player_performances:
            inputs = {RULE_INPUT_VARIABLES.get(performance_type_klass): performance}
            for method in scoring_methods:
                results.append(run_rule(method, inputs, PlayerScoringResult))

    except Exception as ex:
        raise ex

    return results


def score_match(match):
    squads = [match.team_one, match.team_two]
    match_scores = {}

    for squad in squads:
        for player in squad.players.all():
            match_scores[player] = score_performances(player, match)

    return match_scores
