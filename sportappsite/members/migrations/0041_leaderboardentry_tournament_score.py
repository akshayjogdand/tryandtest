# Generated by Django 2.0.2 on 2018-08-03 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0040_remove_leaderboardentry_tournament_score"),
    ]

    operations = [
        migrations.AddField(
            model_name="leaderboardentry",
            name="tournament_score",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
