# Generated by Django 2.0.2 on 2019-07-31 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("predictions", "0083_membersubmission_submission_format")]

    operations = [
        migrations.RenameField(
            model_name="membertournamentprediction",
            old_name="format",
            new_name="prediction_format",
        )
    ]
