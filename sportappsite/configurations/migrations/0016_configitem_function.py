# Generated by Django 3.0.3 on 2020-03-06 23:50

from django.db import migrations
import python_field.python_field


class Migration(migrations.Migration):

    dependencies = [
        ("configurations", "0015_feature_tournaments"),
    ]

    operations = [
        migrations.AddField(
            model_name="configitem",
            name="function",
            field=python_field.python_field.PythonCodeField(
                blank=True, max_length=300, null=True
            ),
        ),
    ]
