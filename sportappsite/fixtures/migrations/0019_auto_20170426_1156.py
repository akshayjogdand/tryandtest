# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-26 11:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fixtures", "0018_match_submissions_allowed"),
    ]

    operations = [
        migrations.AlterField(
            model_name="match",
            name="bat_first_team",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="fixtures.Squad",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="toss_winner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="fixtures.Squad",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="winning_team",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="fixtures.Squad",
            ),
        ),
    ]
