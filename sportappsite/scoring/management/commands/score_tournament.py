from members.models import MemberTournamentPrediction, MemberGroupRules

from IPL_10_Rankings import BOWLER_RANKING, BATSMAN_RANKING, TEAM_RANKING


def get_scoring_methods(member_group):
    return {member_group:
            list(
                MemberGroupRules.objects.filter(
                    member_group=member_group).first()
                .group_tournament_scoring_rules.filter(is_enabled=True))
            }


def group_predictions_by_member_group(predictions):
    grouped = dict()
    for p in predictions:
        try:
            grouped[p.member_group].append(p)
        except KeyError:
            grouped[p.member_group] = []
            grouped[p.member_group].append(p)

    return grouped


def score_tournament(t_id):
    group_member_predictions = group_predictions_by_member_group(
        MemberTournamentPrediction.objects.filter(match=match).all())
    group_scoring_methods = dict()

    try:
        for member_group, predictions in group_member_predictions.items():
            group_scoring_methods.update(
                get_scoring_methods(member_group))

            for prediction in predictions:
                apply_method(prediction,
                             group_scoring_methods[prediction.member_group])
