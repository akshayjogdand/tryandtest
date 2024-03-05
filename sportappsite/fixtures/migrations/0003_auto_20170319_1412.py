# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-19 14:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fixtures", "0002_auto_20170319_1107"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlayerTournamentHistory",
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
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="fixtures.Player",
                    ),
                ),
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="fixtures.Tournament",
                    ),
                ),
            ],
            options={"verbose_name_plural": "Player Tournament histories",},
        ),
        migrations.AlterUniqueTogether(
            name="match", unique_together=set([("tournament", "match_number")]),
        ),
        migrations.AlterUniqueTogether(
            name="playertournamenthistory",
            unique_together=set([("player", "tournament")]),
        ),
    ]
