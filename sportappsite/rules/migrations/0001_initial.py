# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-19 08:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PlayerScoringMethod",
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
                ("name", models.CharField(max_length=100)),
                (
                    "apply_rule_at",
                    models.IntegerField(
                        choices=[
                            (0, "When scoring a Player Performance"),
                            (1, "When validating a Member Prediction"),
                            (2, "When scoring a Member Prediction"),
                        ],
                        default=-1,
                        help_text="When to apply a rule (automatically set on save).",
                    ),
                ),
                (
                    "variables",
                    models.CharField(
                        default="rule, XXX_performance",
                        help_text="Replace XXX_perfromance with any combination of: batting_performance, bowling_performance, fielding_performance, player_match_stats",
                        max_length=100,
                    ),
                ),
                (
                    "calculation",
                    models.TextField(
                        default=" _performance * rule.points_or_factor", max_length=750
                    ),
                ),
                ("points_or_factor", models.IntegerField(default=0)),
                ("is_default", models.BooleanField(default=False)),
                ("is_enabled", models.BooleanField(default=True)),
                ("notes", models.TextField(blank=True, max_length=100, null=True)),
                ("apply_on_batting_performance", models.BooleanField(default=False)),
                ("apply_on_bowling_performance", models.BooleanField(default=False)),
                ("apply_on_fielding_performance", models.BooleanField(default=False)),
                ("apply_on_match_performance", models.BooleanField(default=False)),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="PlayerScoringResult",
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
                ("input_values", models.CharField(default="", max_length=300)),
                ("calculation", models.TextField(default="", max_length=750)),
                ("points_or_factor", models.IntegerField(default=0)),
                ("computed_on", models.DateTimeField(auto_now_add=True)),
                ("result", models.CharField(default="0", max_length=20)),
                (
                    "rule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="rules.PlayerScoringMethod",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="PredictionScoringMethod",
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
                ("name", models.CharField(max_length=100)),
                (
                    "apply_rule_at",
                    models.IntegerField(
                        choices=[
                            (0, "When scoring a Player Performance"),
                            (1, "When validating a Member Prediction"),
                            (2, "When scoring a Member Prediction"),
                        ],
                        default=-1,
                        help_text="When to apply a rule (automatically set on save).",
                    ),
                ),
                (
                    "variables",
                    models.CharField(
                        default="rule, XXX_performance",
                        help_text="Replace XXX_perfromance with any combination of: batting_performance, bowling_performance, fielding_performance, player_match_stats",
                        max_length=100,
                    ),
                ),
                (
                    "calculation",
                    models.TextField(
                        default=" _performance * rule.points_or_factor", max_length=750
                    ),
                ),
                ("points_or_factor", models.IntegerField(default=0)),
                ("is_default", models.BooleanField(default=False)),
                ("is_enabled", models.BooleanField(default=True)),
                ("notes", models.TextField(blank=True, max_length=100, null=True)),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="PredictionScoringResult",
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
                ("input_values", models.CharField(default="", max_length=300)),
                ("calculation", models.TextField(default="", max_length=750)),
                ("points_or_factor", models.IntegerField(default=0)),
                ("computed_on", models.DateTimeField(auto_now_add=True)),
                ("result", models.CharField(default="0", max_length=20)),
                (
                    "rule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="rules.PredictionScoringMethod",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="PredictionSubmissionValidationRule",
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
                ("name", models.CharField(max_length=100)),
                (
                    "apply_rule_at",
                    models.IntegerField(
                        choices=[
                            (0, "When scoring a Player Performance"),
                            (1, "When validating a Member Prediction"),
                            (2, "When scoring a Member Prediction"),
                        ],
                        default=-1,
                        help_text="When to apply a rule (automatically set on save).",
                    ),
                ),
                (
                    "variables",
                    models.CharField(
                        default="rule, XXX_performance",
                        help_text="Replace XXX_perfromance with any combination of: batting_performance, bowling_performance, fielding_performance, player_match_stats",
                        max_length=100,
                    ),
                ),
                (
                    "calculation",
                    models.TextField(
                        default=" _performance * rule.points_or_factor", max_length=750
                    ),
                ),
                ("points_or_factor", models.IntegerField(default=0)),
                ("is_default", models.BooleanField(default=False)),
                ("is_enabled", models.BooleanField(default=True)),
                ("notes", models.TextField(blank=True, max_length=100, null=True)),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="PredictionValidationResult",
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
                ("input_values", models.CharField(default="", max_length=300)),
                ("calculation", models.TextField(default="", max_length=750)),
                ("points_or_factor", models.IntegerField(default=0)),
                ("computed_on", models.DateTimeField(auto_now_add=True)),
                ("result", models.CharField(default="0", max_length=20)),
                (
                    "rule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="rules.PredictionSubmissionValidationRule",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
    ]
