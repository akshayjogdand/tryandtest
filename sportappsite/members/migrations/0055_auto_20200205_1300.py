# Generated by Django 2.0.2 on 2020-02-05 07:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fixtures", "0061_auto_20200123_0854"),
        ("members", "0054_auto_20191126_1848"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="country",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="fixtures.Country",
            ),
        ),
        migrations.AddField(
            model_name="member",
            name="date_of_birth",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="member",
            name="gender",
            field=models.IntegerField(
                blank=True,
                choices=[(1, "Male"), (2, "Female"), (3, "Others")],
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="member",
            name="nick_name",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
