# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-25 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0004_auto_20170325_1227"),
    ]

    operations = [
        migrations.AlterField(
            model_name="membergrouprules",
            name="player_scoring_rules",
            field=models.ManyToManyField(
                blank=True, to="members.GroupPlayerScoringMethod"
            ),
        ),
        migrations.AlterField(
            model_name="membergrouprules",
            name="post_match_prediction_scoring_rules",
            field=models.ManyToManyField(
                blank=True, to="members.GroupPostMatchPredictionScoringMethod"
            ),
        ),
        migrations.AlterField(
            model_name="membergrouprules",
            name="prediction_scoring_rules",
            field=models.ManyToManyField(
                blank=True, to="members.GroupPredictionScoringMethod"
            ),
        ),
        migrations.AlterField(
            model_name="membergrouprules",
            name="prediction_validation_rules",
            field=models.ManyToManyField(
                blank=True, to="members.GroupSubmissionValidationRule"
            ),
        ),
    ]
