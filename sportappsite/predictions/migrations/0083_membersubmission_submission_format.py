# Generated by Django 2.0.3 on 2019-07-30 02:45

from django.db import migrations, models

from sportappsite.constants import MatchTypes

from predictions.models import MemberSubmission as MS


def adjust_existing_submissions(apps, schema_editor):

    for m in MS.objects.filter(submission_type=MS.TOURNAMENT_DATA_SUBMISSION).all():
        if m.tournament.id == 5:
            m.submission_format = 1
        if m.tournament.id == 7:
            m.submission_format = 3

        m.save()

    for m in MS.objects.filter(submission_type=MS.MATCH_DATA_SUBMISSION).all():
        if m.tournament.id == 5:
            m.submission_format = 1
        if m.tournament.id == 7:
            m.submission_format = 3

        m.save()


class Migration(migrations.Migration):

    dependencies = [("predictions", "0082_auto_20190728_0403")]

    operations = [
        migrations.AddField(
            model_name="membersubmission",
            name="submission_format",
            field=models.IntegerField(
                choices=[(1, "One Day"), (2, "T-20"), (3, "Test match")], default=2
            ),
        ),
        migrations.RunPython(adjust_existing_submissions),
    ]
