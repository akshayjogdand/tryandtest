# Generated by Django 3.0.3 on 2021-04-06 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fixtures", "0067_auto_20200826_0924"),
    ]

    operations = [
        migrations.AlterField(
            model_name="playertournamenthistory",
            name="status",
            field=models.IntegerField(
                choices=[(1, "Active"), (2, "Withdrawn"), ("Not playing Matches", 3)],
                default=1,
            ),
        ),
    ]
