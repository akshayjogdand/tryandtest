# Generated by Django 2.0.2 on 2019-12-11 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fixtures", "0053_tournament_abbreviation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tournament",
            name="abbreviation",
            field=models.CharField(default="", max_length=30),
        ),
    ]
