def create_default_submission_fields(member_group, tournament):
    from predictions.models import GroupSubmissionsConfig

    if not GroupSubmissionsConfig.objects.filter(
        member_group=member_group,
        tournament=tournament,
        submission_type=GroupSubmissionsConfig.MATCH_DATA_SUBMISSION,
    ).exists():

        match_fields(member_group, tournament)

    if not GroupSubmissionsConfig.objects.filter(
        member_group=member_group,
        tournament=tournament,
        submission_type=GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION,
    ).exists():

        tournament_fields(member_group, tournament)


def match_fields(member_group, tournament):
    from predictions.models import SubmissionFieldConfig, GroupSubmissionsConfig
    from configurations.models import ConfigItem

    submission_notes = ConfigItem.objects.get(
        tournament=tournament, name="match_prediction_notes_text"
    )

    match_fields_config = GroupSubmissionsConfig()
    match_fields_config.member_group = member_group
    match_fields_config.tournament = tournament
    match_fields_config.submission_notes = submission_notes.value
    match_fields_config.submission_type = GroupSubmissionsConfig.MATCH_DATA_SUBMISSION
    match_fields_config.display_table_ordering = ",".join(
        [
            "submission_time",
            "member",
            "super_player",
            "player_one",
            "player_two",
            "player_three",
            "predicted_winning_team",
            "predicted_winning_team_score",
            "total_wickets",
            "total_fours",
            "total_sixes",
        ]
    )

    match_fields_config.save()

    match_field_1 = SubmissionFieldConfig()
    match_field_1.group_submissions_config = match_fields_config
    match_field_1.form_order = 1
    match_field_1.field = 6
    match_field_1.description = "Player One"
    match_field_1.is_compulsory = True
    match_field_1.is_enabled = True
    match_field_1.enable_for_matches = "lambda match: True"
    match_field_1.field_model = 1
    match_field_1.form_category = None
    match_field_1.save()

    match_field_2 = SubmissionFieldConfig()
    match_field_2.group_submissions_config = match_fields_config
    match_field_2.form_order = 2
    match_field_2.field = 7
    match_field_2.description = "Player Two"
    match_field_2.is_compulsory = True
    match_field_2.is_enabled = True
    match_field_2.enable_for_matches = "lambda match: True"
    match_field_2.field_model = 1
    match_field_2.form_category = None
    match_field_2.save()

    match_field_3 = SubmissionFieldConfig()
    match_field_3.group_submissions_config = match_fields_config
    match_field_3.form_order = 3
    match_field_3.field = 8
    match_field_3.description = "Player Three"
    match_field_3.is_compulsory = True
    match_field_3.is_enabled = True
    match_field_3.enable_for_matches = "lambda match: True"
    match_field_3.field_model = 1
    match_field_3.form_category = None
    match_field_3.save()

    match_field_4 = SubmissionFieldConfig()
    match_field_4.group_submissions_config = match_fields_config
    match_field_4.form_order = 4
    match_field_4.field = 5
    match_field_4.description = "Super Player"
    match_field_4.is_compulsory = True
    match_field_4.is_enabled = True
    match_field_4.enable_for_matches = "lambda match: True"
    match_field_4.field_model = 1
    match_field_4.form_category = None
    match_field_4.save()

    match_field_5 = SubmissionFieldConfig()
    match_field_5.group_submissions_config = match_fields_config
    match_field_5.form_order = 5
    match_field_5.field = 4
    match_field_5.description = "Winning Team"
    match_field_5.is_compulsory = True
    match_field_5.is_enabled = True
    match_field_5.enable_for_matches = "lambda match: True"
    match_field_5.field_model = 0
    match_field_5.form_category = None
    match_field_5.save()

    match_field_6 = SubmissionFieldConfig()
    match_field_6.group_submissions_config = match_fields_config
    match_field_6.form_order = 6
    match_field_6.field = 32
    match_field_6.description = "Winning Team Score"
    match_field_6.is_compulsory = True
    match_field_6.is_enabled = True
    match_field_6.enable_for_matches = "lambda match: True"
    match_field_6.field_model = 3
    match_field_6.form_category = None
    match_field_6.save()

    match_field_7 = SubmissionFieldConfig()
    match_field_7.group_submissions_config = match_fields_config
    match_field_7.form_order = 7
    match_field_7.field = 22
    match_field_7.description = "Total Wickets"
    match_field_7.is_compulsory = True
    match_field_7.is_enabled = True
    match_field_7.enable_for_matches = "lambda match: match.match_number >= 17"
    match_field_7.field_model = 3
    match_field_7.form_category = None
    match_field_7.save()

    match_field_8 = SubmissionFieldConfig()
    match_field_8.group_submissions_config = match_fields_config
    match_field_8.form_order = 8
    match_field_8.field = 31
    match_field_8.description = "Total Fours"
    match_field_8.is_compulsory = True
    match_field_8.is_enabled = True
    match_field_8.enable_for_matches = "lambda match: match.match_number >= 33"
    match_field_8.field_model = 3
    match_field_8.form_category = None
    match_field_8.save()

    match_field_9 = SubmissionFieldConfig()
    match_field_9.group_submissions_config = match_fields_config
    match_field_9.form_order = 9
    match_field_9.field = 30
    match_field_9.description = "Total Sixes"
    match_field_9.is_compulsory = True
    match_field_9.is_enabled = True
    match_field_9.enable_for_matches = "lambda match: match.match_number >= 33"
    match_field_9.field_model = 3
    match_field_9.form_category = None
    match_field_9.save()


TOURNAMENT_NOTES_TEXT = """
This is where you lodge Tournament level Predictions.

You need to complete this by Thursday 30th May 2019 at 09:30 AM BST (08:30 AM UTC).
Till then, change your choices as much as you like!

Please choose:

1. Tournament Winner and Runner Up teams.

2. Third and Fourth placed teams.

3. Worst Performing Team.

4. Top 3 Batsmen in the Tournament.
At least one player has to be from your selected Tournament Winner.

5. Top 3 Bowlers in the Tournament.
At least one player has to be from your selected Tournament Winner.

6. Top 3 “Most Valuable Players" in the Tournament.
At least one player has to be from your selected Tournament Winner.

*** Most Valuable Player is the player who scores most points across all games on FanAboard.

"""


def tournament_fields(member_group, tournament):
    from predictions.models import SubmissionFieldConfig, GroupSubmissionsConfig

    tournament_fields_config = GroupSubmissionsConfig()
    tournament_fields_config.member_group = member_group
    tournament_fields_config.tournament = tournament
    tournament_fields_config.submission_notes = TOURNAMENT_NOTES_TEXT
    tournament_fields_config.submission_type = (
        GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION
    )
    tournament_fields_config.display_table_ordering = ",".join(
        [
            "submission_time",
            "member",
            "tournament_winning_team",
            "runner_up",
            "top_team_three",
            "last_team",
            "top_team_four",
            "top_batsman_one",
            "top_batsman_two",
            "top_batsman_three",
            "top_bowler_one",
            "top_bowler_two",
            "top_bowler_three",
            "most_valuable_player_one",
            "most_valuable_player_two",
            "most_valuable_player_three",
        ]
    )

    tournament_fields_config.save()

    tournament_field_1 = SubmissionFieldConfig()
    tournament_field_1.group_submissions_config = tournament_fields_config
    tournament_field_1.form_order = 1
    tournament_field_1.field = 34
    tournament_field_1.description = "Tournament Winner"
    tournament_field_1.is_compulsory = True
    tournament_field_1.is_enabled = True
    tournament_field_1.enable_for_matches = "lambda match: True"
    tournament_field_1.field_model = 0
    tournament_field_1.form_category = "Tournament Winner and Runner Up"
    tournament_field_1.save()

    tournament_field_2 = SubmissionFieldConfig()
    tournament_field_2.group_submissions_config = tournament_fields_config
    tournament_field_2.form_order = 2
    tournament_field_2.field = 36
    tournament_field_2.description = "Runner Up"
    tournament_field_2.is_compulsory = True
    tournament_field_2.is_enabled = True
    tournament_field_2.enable_for_matches = "lambda match: True"
    tournament_field_2.field_model = 0
    tournament_field_2.form_category = "Tournament Winner and Runner Up"
    tournament_field_2.save()

    tournament_field_3 = SubmissionFieldConfig()
    tournament_field_3.group_submissions_config = tournament_fields_config
    tournament_field_3.form_order = 3
    tournament_field_3.field = 37
    tournament_field_3.description = "Top Team Three"
    tournament_field_3.is_compulsory = True
    tournament_field_3.is_enabled = True
    tournament_field_3.enable_for_matches = "lambda match: True"
    tournament_field_3.field_model = 0
    tournament_field_3.form_category = "Third and Fourth Teams"
    tournament_field_3.save()

    tournament_field_4 = SubmissionFieldConfig()
    tournament_field_4.group_submissions_config = tournament_fields_config
    tournament_field_4.form_order = 4
    tournament_field_4.field = 38
    tournament_field_4.description = "Top Team Four"
    tournament_field_4.is_compulsory = True
    tournament_field_4.is_enabled = True
    tournament_field_4.enable_for_matches = "lambda match: True"
    tournament_field_4.field_model = 0
    tournament_field_4.form_category = "Third and Fourth Teams"
    tournament_field_4.save()

    tournament_field_5 = SubmissionFieldConfig()
    tournament_field_5.group_submissions_config = tournament_fields_config
    tournament_field_5.form_order = 6
    tournament_field_5.field = 39
    tournament_field_5.description = "Top Run Scorer One"
    tournament_field_5.is_compulsory = True
    tournament_field_5.is_enabled = True
    tournament_field_5.enable_for_matches = "lambda match: True"
    tournament_field_5.field_model = 1
    tournament_field_5.form_category = "Top 3 Batsmen"
    tournament_field_5.save()

    tournament_field_6 = SubmissionFieldConfig()
    tournament_field_6.group_submissions_config = tournament_fields_config
    tournament_field_6.form_order = 7
    tournament_field_6.field = 40
    tournament_field_6.description = "Top Run Scorer Two"
    tournament_field_6.is_compulsory = True
    tournament_field_6.is_enabled = True
    tournament_field_6.enable_for_matches = "lambda match: True"
    tournament_field_6.field_model = 1
    tournament_field_6.form_category = "Top 3 Batsmen"
    tournament_field_6.save()

    tournament_field_7 = SubmissionFieldConfig()
    tournament_field_7.group_submissions_config = tournament_fields_config
    tournament_field_7.form_order = 8
    tournament_field_7.field = 41
    tournament_field_7.description = "Top Run Scorer Three"
    tournament_field_7.is_compulsory = True
    tournament_field_7.is_enabled = True
    tournament_field_7.enable_for_matches = "lambda match: True"
    tournament_field_7.field_model = 1
    tournament_field_7.form_category = "Top 3 Batsmen"
    tournament_field_7.save()

    tournament_field_8 = SubmissionFieldConfig()
    tournament_field_8.group_submissions_config = tournament_fields_config
    tournament_field_8.form_order = 9
    tournament_field_8.field = 42
    tournament_field_8.description = "Top Wicket Taker One"
    tournament_field_8.is_compulsory = True
    tournament_field_8.is_enabled = True
    tournament_field_8.enable_for_matches = "lambda match: True"
    tournament_field_8.field_model = 1
    tournament_field_8.form_category = "Top 3 Bowlers"
    tournament_field_8.save()

    tournament_field_9 = SubmissionFieldConfig()
    tournament_field_9.group_submissions_config = tournament_fields_config
    tournament_field_9.form_order = 10
    tournament_field_9.field = 43
    tournament_field_9.description = "Top Wicket Taker Two"
    tournament_field_9.is_compulsory = True
    tournament_field_9.is_enabled = True
    tournament_field_9.enable_for_matches = "lambda match: True"
    tournament_field_9.field_model = 1
    tournament_field_9.form_category = "Top 3 Bowlers"
    tournament_field_9.save()

    tournament_field_10 = SubmissionFieldConfig()
    tournament_field_10.group_submissions_config = tournament_fields_config
    tournament_field_10.form_order = 11
    tournament_field_10.field = 44
    tournament_field_10.description = "Top Wicket Taker Three"
    tournament_field_10.is_compulsory = True
    tournament_field_10.is_enabled = True
    tournament_field_10.enable_for_matches = "lambda match: True"
    tournament_field_10.field_model = 1
    tournament_field_10.form_category = "Top 3 Bowlers"
    tournament_field_10.save()

    tournament_field_11 = SubmissionFieldConfig()
    tournament_field_11.group_submissions_config = tournament_fields_config
    tournament_field_11.form_order = 12
    tournament_field_11.field = 45
    tournament_field_11.description = "Most Valuable Player One"
    tournament_field_11.is_compulsory = True
    tournament_field_11.is_enabled = True
    tournament_field_11.enable_for_matches = "lambda match: True"
    tournament_field_11.field_model = 1
    tournament_field_11.form_category = "Most Valuable Players"
    tournament_field_11.save()

    tournament_field_12 = SubmissionFieldConfig()
    tournament_field_12.group_submissions_config = tournament_fields_config
    tournament_field_12.form_order = 13
    tournament_field_12.field = 46
    tournament_field_12.description = "Most Valuable Player Two"
    tournament_field_12.is_compulsory = True
    tournament_field_12.is_enabled = True
    tournament_field_12.enable_for_matches = "lambda match: True"
    tournament_field_12.field_model = 1
    tournament_field_12.form_category = "Most Valuable Players"
    tournament_field_12.save()

    tournament_field_13 = SubmissionFieldConfig()
    tournament_field_13.group_submissions_config = tournament_fields_config
    tournament_field_13.form_order = 14
    tournament_field_13.field = 47
    tournament_field_13.description = "Most Valuable Player Three"
    tournament_field_13.is_compulsory = True
    tournament_field_13.is_enabled = True
    tournament_field_13.enable_for_matches = "lambda match: True"
    tournament_field_13.field_model = 1
    tournament_field_13.form_category = "Most Valuable Players"
    tournament_field_13.save()

    tournament_field_14 = SubmissionFieldConfig()
    tournament_field_14.group_submissions_config = tournament_fields_config
    tournament_field_14.form_order = 5
    tournament_field_14.field = 48
    tournament_field_14.description = "Last Team"
    tournament_field_14.is_compulsory = True
    tournament_field_14.is_enabled = True
    tournament_field_14.enable_for_matches = "lambda match: True"
    tournament_field_14.field_model = 0
    tournament_field_14.form_category = "Worst Performing Team"
    tournament_field_14.save()
