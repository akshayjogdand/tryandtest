from django.core.management.base import BaseCommand

from fixtures.models import Match, Tournament


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        tournament = Tournament.objects.get(id=5)
        finals_map = {144: 46, 148: 48, 166: 47}

        for match in Match.objects.filter(tournament=tournament).order_by("match_date"):
            old_name = match.name

            if (
                "Eliminator" not in old_name
                and "Qualifier" not in old_name
                and "Final" not in old_name
            ):

                new_number = ""
                for i in match.reference_name:
                    if i.isnumeric():
                        new_number = new_number + i
                        match.match_number = int(new_number)
            else:
                match.match_number = 0

            if match.team_one and match.team_two:
                new_name = "{}, {}: {} vs {}".format(
                    match.tournament.name,
                    match.reference_name,
                    match.team_one.team.name,
                    match.team_two.team.name,
                )
            else:
                new_name = "{}, {}".format(match.tournament, match.reference_name)

            match.name = new_name

            if match.id in finals_map:
                match.match_number = finals_map[match.id]

            # self.stdout.write('Changing {}\nfrom: {}\nto: {}\nmatch number is: {}\n'.format(
            #    match, old_name, new_name, match.match_number))

            match.save()
