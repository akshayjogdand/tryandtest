# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-03-02 14:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("live_scores", "0003_auto_20180302_0347"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ballbyball",
            name="comments",
            field=models.CharField(max_length=10000, null=True),
        ),
    ]
