# Generated by Django 2.0.2 on 2019-05-26 04:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0048_groupleaderboard_show_ts_column"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="member", options={"ordering": ("user__first_name",)},
        ),
        migrations.AlterModelOptions(
            name="membership", options={"ordering": ("member__user__first_name",)},
        ),
    ]
