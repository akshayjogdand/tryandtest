# Generated by Django 2.0.2 on 2018-04-03 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fixtures", "0029_match_reference_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="match",
            name="name",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
