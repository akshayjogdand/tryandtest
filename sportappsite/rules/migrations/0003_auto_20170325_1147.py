# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-25 11:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rules", "0002_auto_20170325_0904"),
    ]

    operations = [
        migrations.AlterField(
            model_name="playerscoringmethod",
            name="apply_rule_at",
            field=models.IntegerField(
                choices=[
                    (0, "When scoring a Player Performance"),
                    (1, "When validating a Member Prediction"),
                    (2, "When scoring a Member Prediction"),
                    (
                        3,
                        "Apply after Match is finished and\n                                        all Predictions have been scored",
                    ),
                ],
                default=-1,
                help_text="When to apply a rule (automatically set on save).",
            ),
        ),
        migrations.AlterField(
            model_name="playerscoringmethod",
            name="variables",
            field=models.CharField(
                default="rule, XXX_performance",
                help_text="Replace XXX_perfromance with any combination of:\n                      batting_performance, bowling_performance,\n                      fielding_performance, player_match_stats",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="postmatchpredictionscoringmethod",
            name="apply_rule_at",
            field=models.IntegerField(
                choices=[
                    (0, "When scoring a Player Performance"),
                    (1, "When validating a Member Prediction"),
                    (2, "When scoring a Member Prediction"),
                    (
                        3,
                        "Apply after Match is finished and\n                                        all Predictions have been scored",
                    ),
                ],
                default=-1,
                help_text="When to apply a rule (automatically set on save).",
            ),
        ),
        migrations.AlterField(
            model_name="postmatchpredictionscoringmethod",
            name="variables",
            field=models.CharField(
                default="rule, XXX_performance",
                help_text="Replace XXX_perfromance with any combination of:\n                      batting_performance, bowling_performance,\n                      fielding_performance, player_match_stats",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="predictionscoringmethod",
            name="apply_rule_at",
            field=models.IntegerField(
                choices=[
                    (0, "When scoring a Player Performance"),
                    (1, "When validating a Member Prediction"),
                    (2, "When scoring a Member Prediction"),
                    (
                        3,
                        "Apply after Match is finished and\n                                        all Predictions have been scored",
                    ),
                ],
                default=-1,
                help_text="When to apply a rule (automatically set on save).",
            ),
        ),
        migrations.AlterField(
            model_name="predictionscoringmethod",
            name="variables",
            field=models.CharField(
                default="rule, XXX_performance",
                help_text="Replace XXX_perfromance with any combination of:\n                      batting_performance, bowling_performance,\n                      fielding_performance, player_match_stats",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="predictionsubmissionvalidationrule",
            name="apply_rule_at",
            field=models.IntegerField(
                choices=[
                    (0, "When scoring a Player Performance"),
                    (1, "When validating a Member Prediction"),
                    (2, "When scoring a Member Prediction"),
                    (
                        3,
                        "Apply after Match is finished and\n                                        all Predictions have been scored",
                    ),
                ],
                default=-1,
                help_text="When to apply a rule (automatically set on save).",
            ),
        ),
        migrations.AlterField(
            model_name="predictionsubmissionvalidationrule",
            name="variables",
            field=models.CharField(
                default="rule, XXX_performance",
                help_text="Replace XXX_perfromance with any combination of:\n                      batting_performance, bowling_performance,\n                      fielding_performance, player_match_stats",
                max_length=100,
            ),
        ),
    ]
