# MEMBER_PREDICTION_SCORING
apply_rule_at = 2

points_or_factor = 1
rule_category = 4

# ONE_DAY
apply_to_match_type = 1

variables = ("match", "prediction", "rule")

enable_for_matches = lambda match: True


def winning_score_range(match, prediction):

    if match.winning_team is None:
        return 0

    if match.winning_team.team != prediction.predicted_winning_team:
        return 0

    if prediction.predicted_winning_team_score is None:
        return 0

    if match.winning_team.team == prediction.winning_team:

        if match.winning_score == prediction.predicted_winning_team_score:
            return 400

        if match.calculated_winning_score == (prediction.predicted_winning_team_score):
            return 400

        if match.final_winning_score == (prediction.predicted_winning_team_score):
            return 400

        if match.dl_calculated_winning_score == (
            prediction.predicted_winning_team_score
        ):
            return 400

        if (
            (match.winning_score != prediction.predicted_winning_team_score)
            and (
                match.calculated_winning_score
                != prediction.predicted_winning_team_score
            )
            and (match.final_winning_score != prediction.predicted_winning_team_score)
            and (
                match.dl_calculated_winning_score
                != prediction.predicted_winning_team_score
            )
        ):

            if abs(match.winning_score - prediction.predicted_winning_team_score) <= 10:
                return 100

            elif (
                abs(
                    match.calculated_winning_score
                    - prediction.predicted_winning_team_score
                )
                <= 10
            ):
                return 100

            elif (
                abs(match.final_winning_score - prediction.predicted_winning_team_score)
                <= 10
            ):
                return 100

            elif (
                abs(
                    match.dl_calculated_winning_score
                    - prediction.predicted_winning_team_score
                )
                <= 10
            ):
                return 100

            elif (
                abs(match.winning_score - prediction.predicted_winning_team_score) <= 20
            ):
                return 50

            elif (
                abs(
                    match.calculated_winning_score
                    - prediction.predicted_winning_team_score
                )
                <= 20
            ):
                return 50

            elif (
                abs(match.final_winning_score - prediction.predicted_winning_team_score)
                <= 20
            ):
                return 50

            elif (
                abs(
                    match.dl_calculated_winning_score
                    - prediction.predicted_winning_team_score
                )
                <= 20
            ):
                return 50

            else:
                return 0

        else:
            return 0

    else:
        return 0


calculation = lambda: winning_score_range(match, prediction) * rule.points_or_factor
