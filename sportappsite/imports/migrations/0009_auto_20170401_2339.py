# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-01 23:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("imports", "0008_auto_20170401_2332"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dataimport",
            name="import_type",
            field=models.IntegerField(
                choices=[
                    (0, "Match data"),
                    (1, "Batting Performance"),
                    (2, "Bowling Performance"),
                    (3, "Fielding Performance"),
                    (4, "Match Performance"),
                    (5, "Member Predictions"),
                ]
            ),
        ),
    ]
