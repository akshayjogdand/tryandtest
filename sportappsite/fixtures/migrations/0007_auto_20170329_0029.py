# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-29 00:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fixtures", "0006_auto_20170328_1304"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tournamentdefaultrules",
            options={"verbose_name_plural": "Tournament Default Rules"},
        ),
    ]
