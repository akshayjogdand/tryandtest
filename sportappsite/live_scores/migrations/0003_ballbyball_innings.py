# Generated by Django 2.0.2 on 2019-08-07 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("live_scores", "0002_auto_20180408_0744"),
    ]

    operations = [
        migrations.AddField(
            model_name="ballbyball",
            name="innings",
            field=models.IntegerField(default=1),
        ),
    ]
