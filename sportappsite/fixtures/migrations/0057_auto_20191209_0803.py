# Generated by Django 2.0.2 on 2019-12-09 08:03

from django.db import migrations
import python_field.python_field
import python_field.utils


class Migration(migrations.Migration):

    dependencies = [
        ("fixtures", "0056_auto_20191209_0554"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tournament",
            name="match_naming_strategy",
            field=python_field.python_field.PythonCodeField(
                default="lambda match: '{}, {}: {} vs. {}'.format(match.tournament.name, match.reference_name, match.team_one.team.name, match.team_two.team.name)",
                max_length=200,
                validators=[python_field.utils.is_code_and_lambda],
            ),
        ),
        migrations.AlterField(
            model_name="tournament",
            name="short_display_name_strategy",
            field=python_field.python_field.PythonCodeField(
                default="lambda match: '{}, {}: {} vs. {}'.format(match.tournament.name, match.reference_name, match.team_one.team.abbreviation, match.team_two.team.abbreviation)",
                max_length=200,
                validators=[python_field.utils.is_code_and_lambda],
            ),
        ),
    ]
