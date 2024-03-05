# Generated by Django 2.0.2 on 2019-08-13 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fixtures", "0045_auto_20190801_0549"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="fourth_innings_bowled",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_byes",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_catches",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_extras",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_fours",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_free_hits",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_lbws",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_legbyes",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_noballs",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_penalties",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_runouts",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_sixes",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_stumpings",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="fourth_innings_wides",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_bowled",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_byes",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_catches",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_extras",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_fours",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_free_hits",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_lbws",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_legbyes",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_noballs",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_penalties",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_runouts",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_sixes",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_stumpings",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="match",
            name="third_innings_wides",
            field=models.IntegerField(default=0),
        ),
    ]
