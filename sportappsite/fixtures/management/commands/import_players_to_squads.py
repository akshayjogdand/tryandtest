import csv

from django.core.management.base import BaseCommand, CommandError

from fixtures.models import Player, Squad, Team


class Command(BaseCommand):
    help = "Load a list of Players from a CSV file into a Squad"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-file", required=True, type=str, help="path to CSV file"
        )
        parser.add_argument(
            "--team-id", required=True, type=int, help="Team to which player belongs"
        )

    def handle(self, csv_file, team_id, *args, **options):
        try:
            team = Team.objects.get(id=team_id)
            squads = Squad.objects.filter(team=team).order_by("-squad_number")

            squad = Squad()
            squad.team = team
            squad.squad_number = squads[0].squad_number + 1
            squad.save()

            with open(csv_file) as fil:
                reader = csv.DictReader(fil)
                for row in reader:
                    name = row["name"].strip()
                    try:
                        p = Player.objects.get(name=name)
                    except Player.DoesNotExist:
                        p = Player()
                        p.name = name
                        p.save()

                    squad.players.add(p)
            squad.save()
        except Exception as e:
            raise CommandError(e)
        else:
            self.stdout.write("Loaded players from: {}".format(csv_file))
            self.stdout.write("New squad ID is: {}".format(squad.id))
