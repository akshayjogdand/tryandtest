# Generated by Django 2.0.2 on 2020-01-08 03:58

from django.db import migrations, models
import python_field.python_field


class Migration(migrations.Migration):

    dependencies = [("predictions", "0097_auto_20191209_0545")]

    operations = [
        migrations.AddField(
            model_name="submissionfieldconfig",
            name="is_reactive",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="submissionfieldconfig",
            name="reaction_targets",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="submissionfieldconfig",
            name="reactions",
            field=python_field.python_field.PythonCodeField(
                blank=True,
                help_text=(
                    "[ { 'name': 'Disable on Tie', ",
                    "    'match_regex': 'lambda submission_config: \"^xx$\"', ",
                    "    'field_value': '0', ",
                    "    'field_status: 'disabled' } ] ",
                ),
                max_length=500,
                null=True,
            ),
        ),
    ]
