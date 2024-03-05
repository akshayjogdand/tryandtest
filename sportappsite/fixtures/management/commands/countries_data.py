from django.core.management.base import BaseCommand, CommandError
import os
import json
from fixtures.models import Country
from drf_api.serializers import CountrySerializer
from django.core import serializers
from django.http import HttpResponse
import json


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--action",
            required=True,
            type=str,
            help="Type action you want perform. It should be either import or export",
        )

        parser.add_argument(
            "--path",
            required=True,
            type=str,
            help="If importing to countries model then pass file path",
        )

    def handle(self, action, path, **options):

        if action == "import":
            import_countries_data(path)

        if action == "export":
            export_countries_data(path)


def import_countries_data(path):

    if len(path) == 0:
        print("please mention the path")

    else:

        file = open(path, "r+")
        file_reader = file.read()

        data = ""
        for i in file_reader:
            data += i

        countries = json.loads(data)
        file.close()

        for c in countries:
            cds = Country.objects.filter(name=c["country_name"])
            cd = Country()
            if cds.count() == 0:
                cd.name = c["country_name"]
                cd.code = c["country_code"]
                cd.calling_code = c["dialling_code"]
            else:
                cd = cds[0]
                cd.name = c["country_name"]
                cd.code = c["country_code"]
                cd.calling_code = c["dialling_code"]
            cd.save()

        print("Data Imported sucessfully")


def export_countries_data(path):
    if len(path) == 0:
        print("please mention the path")

    else:
        cd = Country.objects.all()
        country_data = CountrySerializer(cd, many=True).data
        file_name = "countries_data.json"
        file = open(path + file_name, "w+")
        file.write(json.dumps(country_data))
        file.close()
        print("Data Exported sucessfully")
