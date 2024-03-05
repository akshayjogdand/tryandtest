# Generated by Django 2.0.3 on 2019-08-13 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("predictions", "0086_membertournamentprediction_win_series_margin")
    ]

    operations = [
        migrations.AddField(
            model_name="memberprediction",
            name="first_inning_run_lead",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="submissionfieldconfig",
            name="field",
            field=models.IntegerField(
                choices=[
                    (4, "predicted_winning_team"),
                    (5, "super_player"),
                    (6, "player_one"),
                    (7, "player_two"),
                    (8, "player_three"),
                    (9, "player_four"),
                    (10, "player_five"),
                    (11, "toss_winner"),
                    (12, "toss_outcome"),
                    (13, "toss_decision"),
                    (14, "player_with_most_sixes"),
                    (15, "player_with_most_fours"),
                    (16, "player_with_most_runs"),
                    (17, "player_with_most_wickets"),
                    (18, "total_extras"),
                    (19, "total_free_hits"),
                    (20, "total_run_outs"),
                    (21, "total_catches"),
                    (22, "total_wickets"),
                    (23, "total_wides"),
                    (24, "total_noballs"),
                    (25, "total_byes"),
                    (26, "total_legbyes"),
                    (27, "total_bowled"),
                    (28, "total_stumpings"),
                    (29, "total_lbws"),
                    (30, "total_sixes"),
                    (31, "total_fours"),
                    (32, "predicted_winning_team_score"),
                    (33, "predicted_first_wicket_gone_in_over"),
                    (34, "tournament_winning_team"),
                    (36, "runner_up"),
                    (37, "top_team_three"),
                    (38, "top_team_four"),
                    (39, "top_batsman_one"),
                    (40, "top_batsman_two"),
                    (41, "top_batsman_three"),
                    (42, "top_bowler_one"),
                    (43, "top_bowler_two"),
                    (44, "top_bowler_three"),
                    (45, "most_valuable_player_one"),
                    (46, "most_valuable_player_two"),
                    (47, "most_valuable_player_three"),
                    (48, "last_team"),
                    (49, "win_series_margin"),
                    (50, "first_inning_runs_lead"),
                ]
            ),
        ),
    ]
