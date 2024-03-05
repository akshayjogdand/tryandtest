# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-20 11:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stats", "0001_initial"),
        ("members", "0001_initial"),
        ("fixtures", "0004_playertournamenthistory_team"),
        ("predictions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MemberPrediction",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("predicted_winning_team_score", models.IntegerField(default=0)),
                ("total_extras", models.IntegerField(blank=True, null=True)),
                ("total_free_hits", models.IntegerField(blank=True, null=True)),
                ("total_run_outs", models.IntegerField(blank=True, null=True)),
                ("total_catches", models.IntegerField(blank=True, null=True)),
                ("total_wickets", models.IntegerField(blank=True, null=True)),
                ("total_wides", models.IntegerField(blank=True, null=True)),
                ("total_noballs", models.IntegerField(blank=True, null=True)),
                ("total_byes", models.IntegerField(blank=True, null=True)),
                ("total_legbyes", models.IntegerField(blank=True, null=True)),
                ("total_bowled", models.IntegerField(blank=True, null=True)),
                ("total_stumpings", models.IntegerField(blank=True, null=True)),
                ("total_lbws", models.IntegerField(blank=True, null=True)),
                ("total_sixes", models.IntegerField(blank=True, null=True)),
                ("total_fours", models.IntegerField(blank=True, null=True)),
                ("prediction_has_been_scored", models.BooleanField(default=False)),
                ("prediction_submissions_locked", models.BooleanField(default=False)),
                ("total_prediction_score", models.IntegerField(default=0)),
                (
                    "winning_team",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("winning_team_score", models.IntegerField(blank=True, null=True)),
                (
                    "winning_team_calculated_winning_score",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "winning_team_final_winning_score",
                    models.IntegerField(blank=True, null=True),
                ),
                (
                    "batsman_with_most_fours",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="fixtures.Player",
                    ),
                ),
                (
                    "batsman_with_most_sixes",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="fixtures.Player",
                    ),
                ),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="fixtures.Match",
                    ),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="members.Member",
                    ),
                ),
                (
                    "member_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="members.MemberGroup",
                    ),
                ),
                (
                    "player_one",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="fixtures.Player",
                    ),
                ),
                (
                    "player_one_score",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="stats.PlayerScores",
                    ),
                ),
                (
                    "player_three",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="fixtures.Player",
                    ),
                ),
                (
                    "player_three_score",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="stats.PlayerScores",
                    ),
                ),
                (
                    "player_two",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="fixtures.Player",
                    ),
                ),
                (
                    "player_two_score",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="stats.PlayerScores",
                    ),
                ),
                (
                    "predicted_winning_team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="fixtures.Team",
                    ),
                ),
            ],
        ),
        migrations.AlterModelOptions(
            name="predictionscores",
            options={"verbose_name_plural": "Prediction scores"},
        ),
        migrations.AlterField(
            model_name="predictionscores",
            name="Prediction",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="predictions.MemberPrediction",
            ),
        ),
        migrations.AlterField(
            model_name="predictionvalidations",
            name="Prediction",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="predictions.MemberPrediction",
            ),
        ),
        migrations.AddField(
            model_name="memberprediction",
            name="prediction_score",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="predictions.PredictionScores",
            ),
        ),
        migrations.AddField(
            model_name="memberprediction",
            name="super_player",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="fixtures.Player",
            ),
        ),
        migrations.AddField(
            model_name="memberprediction",
            name="toss_winner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="fixtures.Team",
            ),
        ),
    ]
