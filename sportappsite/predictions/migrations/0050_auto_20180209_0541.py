# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-02-09 05:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("predictions", "0049_auto_20180208_1148")]

    operations = [
        migrations.RenameModel(
            old_name="PredictionValidations", new_name="PredictionSubmissionValidations"
        )
    ]
