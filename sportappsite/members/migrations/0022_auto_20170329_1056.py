# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-29 10:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0021_auto_20170329_0539"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="groupleaderboard", options={"ordering": ["board_number"]},
        ),
        migrations.AlterField(
            model_name="groupleaderboard",
            name="board_number",
            field=models.IntegerField(default=0),
        ),
    ]
