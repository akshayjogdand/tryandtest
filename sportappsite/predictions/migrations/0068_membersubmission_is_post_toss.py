# Generated by Django 2.0.2 on 2018-04-23 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("predictions", "0067_auto_20180423_0647")]

    operations = [
        migrations.AddField(
            model_name="membersubmission",
            name="is_post_toss",
            field=models.BooleanField(default=False),
        )
    ]
