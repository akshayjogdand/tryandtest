import csv

from django.core.management.base import BaseCommand

from django.db import transaction

from fixtures.models import Player, Team, PlayerTournamentHistory, Tournament, Country


class Command(BaseCommand):
    help = "Load a list of Players from a CSV and "
    "associate with Team and Tournament"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-file", required=True, type=str, help="path to CSV file"
        )

    @transaction.atomic
    def handle(self, csv_file, *args, **options):
        try:
            with open(csv_file) as fil:
                reader = csv.DictReader(fil)
                for row in reader:
                    country = Country.objects.get(name=row.get("country"))
                    team = Team.objects.get(id=row.get("team_id"))
                    tournament = Tournament.objects.get(id=row.get("tournament_id"))

                    try:
                        name = row.get("player_name").strip()
                        print("Importing {}".format(name))
                        p = Player.objects.get(name=name)
                        p.country = country
                        p.save()
                    except Player.DoesNotExist:
                        p = Player()
                        p.name = name
                        p.country = country
                        p.save()

                    th = PlayerTournamentHistory()
                    th.tournament = tournament
                    th.player = p
                    th.team = team
                    th.save()

        except Exception as e:
            raise e
        else:
            self.stdout.write("Loaded players from: {}".format(csv_file))
