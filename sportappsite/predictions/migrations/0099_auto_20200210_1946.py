# Generated by Django 2.0.2 on 2020-02-10 14:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("predictions", "0098_auto_20200110_1741"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="membersubmission", name="predictions_member__983558_idx",
        ),
    ]
