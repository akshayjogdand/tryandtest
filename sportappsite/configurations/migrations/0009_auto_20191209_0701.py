# Generated by Django 2.0.3 on 2019-12-09 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("configurations", "0008_auto_20190610_0115")]

    operations = [
        migrations.AlterField(
            model_name="matchsubmissionnotes",
            name="name",
            field=models.CharField(max_length=100),
        )
    ]
