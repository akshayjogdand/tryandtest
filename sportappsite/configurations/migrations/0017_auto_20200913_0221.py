# Generated by Django 3.0.3 on 2020-09-13 02:21

from django.db import migrations, models
import fixtures.models
import python_field.python_field
import python_field.utils


class Migration(migrations.Migration):

    dependencies = [
        ("configurations", "0016_configitem_function"),
    ]

    operations = [
        migrations.AddField(
            model_name="feature",
            name="data",
            field=python_field.python_field.PythonCodeField(
                default="lambda s: {'individual_contribution_amount: 0}",
                max_length=200,
                validators=[python_field.utils.is_code_and_lambda],
            ),
        ),
        migrations.AddField(
            model_name="feature",
            name="tournament_format",
            field=models.IntegerField(
                blank=True,
                choices=[(1, "One Day"), (2, "T-20"), (3, "Test match")],
                default=fixtures.models.TournamentFormats["T_TWENTY"],
                null=True,
            ),
        ),
    ]
