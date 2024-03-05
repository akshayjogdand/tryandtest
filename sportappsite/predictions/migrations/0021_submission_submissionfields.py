# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-12 12:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fixtures", "0017_auto_20170408_0131"),
        ("members", "0023_auto_20170409_1058"),
        ("predictions", "0020_auto_20170404_1048"),
    ]

    operations = [
        migrations.CreateModel(
            name="Submission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("submission_time", models.DateTimeField(auto_now_add=True)),
                ("is_valid", models.BooleanField(default=False)),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="members.Member"
                    ),
                ),
                (
                    "member_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="members.MemberGroup",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SubmissionFields",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("field", models.CharField(max_length=100)),
                ("value", models.IntegerField(blank=True, null=True)),
                (
                    "player",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="fixtures.Player",
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="predictions.Submission",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="fixtures.Team",
                    ),
                ),
            ],
        ),
    ]
