# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-04 13:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fixtures", "0015_auto_20170404_1055"),
    ]

    operations = [
        migrations.RenameField(
            model_name="match",
            old_name="first_innings_lbw",
            new_name="first_innings_lbws",
        ),
        migrations.RenameField(
            model_name="match",
            old_name="second_innings_lbw",
            new_name="second_innings_lbws",
        ),
    ]
