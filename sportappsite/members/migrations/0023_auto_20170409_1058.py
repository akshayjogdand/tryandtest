# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-09 10:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0022_auto_20170329_1056"),
    ]

    operations = [
        migrations.RenameField(
            model_name="leaderboardentry",
            old_name="initial_points",
            new_name="previous_points",
        ),
    ]
