# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-27 13:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("predictions", "0034_auto_20170525_1302")]

    operations = [
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
                ]
            ),
        )
    ]
