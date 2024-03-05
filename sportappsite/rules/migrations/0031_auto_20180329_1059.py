# Generated by Django 2.0.2 on 2018-03-29 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rules", "0030_auto_20180316_0422"),
    ]

    operations = [
        migrations.AddField(
            model_name="groupleaderboardscoringmethod",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
        migrations.AddField(
            model_name="groupplayerscoringmethod",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
        migrations.AddField(
            model_name="grouppostmatchpredictionscoringmethod",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
        migrations.AddField(
            model_name="grouppredictionscoringmethod",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
        migrations.AddField(
            model_name="grouppredictionsubmissionvalidationrule",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
        migrations.AddField(
            model_name="grouptournamentscoringmethod",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
        migrations.AddField(
            model_name="leaderboardscoringmethod",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
        migrations.AddField(
            model_name="playerscoringmethod",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
        migrations.AddField(
            model_name="postmatchpredictionscoringmethod",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
        migrations.AddField(
            model_name="predictionscoringmethod",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
        migrations.AddField(
            model_name="predictionsubmissionvalidationrule",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
        migrations.AddField(
            model_name="tournamentscoringmethod",
            name="rule_category",
            field=models.IntegerField(
                choices=[
                    (-1, "---"),
                    (0, "Batting Points"),
                    (1, "Bowling Points"),
                    (2, "Fielding Points"),
                    (3, "General Points"),
                ],
                default=-1,
            ),
        ),
    ]
