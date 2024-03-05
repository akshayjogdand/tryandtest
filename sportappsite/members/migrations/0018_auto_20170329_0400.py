# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-29 04:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0017_auto_20170329_0356"),
    ]

    operations = [
        migrations.AlterField(
            model_name="leaderboardentry",
            name="leader_board",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="entries",
                to="members.GroupLeaderBoard",
            ),
        ),
    ]
