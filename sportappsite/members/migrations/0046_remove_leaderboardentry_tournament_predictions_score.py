# Generated by Django 2.0.2 on 2018-08-04 03:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0045_auto_20180804_0012"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="leaderboardentry", name="tournament_predictions_score",
        ),
    ]
