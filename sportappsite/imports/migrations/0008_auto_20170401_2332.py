# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-01 23:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("imports", "0007_auto_20170401_1242"),
    ]

    operations = [
        migrations.RenameField(
            model_name="dataimport", old_name="fname", new_name="data_file",
        ),
    ]
