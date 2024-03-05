import csv
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from fixtures.models import Player, Match, Tournament, Venue, Squad
from stats.models import (
    BattingPerformance,
    BowlingPerformance,
    FieldingPerformance,
    MatchPerformance,
)

TYPE_MAP = {
    "bowling": BowlingPerformance,
    "batting": BattingPerformance,
    "fielding": FieldingPerformance,
    "match-stats": MatchPerformance,
    "match": Match,
}

VALUE_MAP = {"TRUE": True, "FALSE": False}


def parse_players(value):
    players = []
    names = filter(lambda s: s != "", value.split("||"))
    for name in names:
        p = Player.objects.get(name=name.strip())
        players.append(p)

    return players


def clean(value):
    v = value.strip()

    if v in VALUE_MAP:
        return VALUE_MAP[v]
    try:
        c = int(v)
    except:
        if v == "":
            return 0
        else:
            return v
    else:
        return c


class Command(BaseCommand):
    help = "Load Batting Performances from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--performance-type",
            required=True,
            type=str,
            choices=TYPE_MAP.keys(),
            help="performance type",
        )
        parser.add_argument(
            "--csv-file", required=True, type=str, help="path to CSV file"
        )
        parser.add_argument(
            "--match-id",
            type=int,
            nargs="?",
            help="Match ID to load data against,"
            "(not required for performance_type=match)",
        )

    def handle(self, performance_type, csv_file, match_id, *args, **options):
        klass = TYPE_MAP[performance_type]
        if klass == Match:
            self.import_match(csv_file, match_id)
        else:
            self.import_performance(performance_type, klass, csv_file, match_id)

    @transaction.atomic
    def import_match(self, csv_file, match_id):
        try:
            fil = open(csv_file)
            reader = csv.DictReader(fil)

            for row in reader:

                match = Match.objects.get(id=match_id)
                match.tournament = Tournament.objects.get(
                    id=clean(row.pop("tournament"))
                )
                match.venue = Venue.objects.get(id=clean(row.pop("venue")))
                match.match_date = datetime.datetime.strptime(
                    row.pop("match_date"), "%d/%m/%Y"
                )
                match.match_number = clean(row.pop("match_number"))
                match.match_type = getattr(Match, row.pop("match_type"))
                match.match_status = getattr(Match, row.pop("match_status"))
                match.match_result = getattr(Match, row.pop("match_result"))
                match.toss_winner = Squad.objects.get(id=clean(row.pop("toss_winner")))
                match.toss_outcome = getattr(Match, row.pop("toss_outcome"))
                match.toss_decision = getattr(Match, row.pop("toss_decision"))
                match.team_one = Squad.objects.get(id=clean(row.pop("team_one")))
                match.team_two = Squad.objects.get(id=clean(row.pop("team_two")))

                match.first_innings_runs = clean(row.pop("first_innings_runs"))
                match.first_innings_overs = clean(row.pop("first_innings_overs"))
                match.first_innings_balls = clean(row.pop("first_innings_balls"))
                match.first_innings_wickets = clean(row.pop("first_innings_wickets"))
                match.first_innings_fours = clean(row.pop("first_innings_fours"))
                match.first_innings_sixes = clean(row.pop("first_innings_sixes"))
                match.first_innings_extras = clean(row.pop("first_innings_extras"))
                match.first_innings_noballs = clean(row.pop("first_innings_noballs"))
                match.first_innings_wides = clean(row.pop("first_innings_wides"))
                match.first_innings_byes = clean(row.pop("first_innings_byes"))
                match.first_innings_legbyes = clean(row.pop("first_innings_legbyes"))
                match.first_innings_penalties = clean(
                    row.pop("first_innings_penalties")
                )
                match.first_innings_catches = clean(row.pop("first_innings_catches"))
                match.first_innings_stumpings = clean(
                    row.pop("first_innings_stumpings")
                )
                match.first_innings_runouts = clean(row.pop("first_innings_runouts"))
                match.first_innings_free_hits = clean(
                    row.pop("first_innings_free_hits")
                )
                match.first_innings_lbws = clean(row.pop("first_innings_lbws"))
                match.first_innings_bowled = clean(row.pop("first_innings_bowled"))

                match.second_innings_free_hits = clean(
                    row.pop("second_innings_free_hits")
                )
                match.second_innings_lbws = clean(row.pop("second_innings_lbws"))
                match.second_innings_bowled = clean(row.pop("second_innings_bowled"))
                match.second_innings_runs = clean(row.pop("second_innings_runs"))
                match.second_innings_overs = clean(row.pop("second_innings_overs"))
                match.second_innings_balls = clean(row.pop("second_innings_balls"))
                match.second_innings_wickets = clean(row.pop("second_innings_wickets"))
                match.second_innings_fours = clean(row.pop("second_innings_fours"))
                match.second_innings_sixes = clean(row.pop("second_innings_sixes"))
                match.second_innings_extras = clean(row.pop("second_innings_extras"))
                match.second_innings_noballs = clean(row.pop("second_innings_noballs"))
                match.second_innings_wides = clean(row.pop("second_innings_wides"))
                match.second_innings_byes = clean(row.pop("second_innings_byes"))
                match.second_innings_legbyes = clean(row.pop("second_innings_legbyes"))
                match.second_innings_penalties = clean(
                    row.pop("second_innings_penalties")
                )
                match.second_innings_catches = clean(row.pop("second_innings_catches"))
                match.second_innings_stumpings = clean(
                    row.pop("second_innings_stumpings")
                )
                match.second_innings_runouts = clean(row.pop("second_innings_runouts"))

                match.maximum_overs = clean(row.pop("maximum_overs"))
                match.maximum_overs_balls = clean(row.pop("maximum_overs_balls"))
                match.final_overs = clean(row.pop("final_overs"))
                match.final_overs_balls = clean(row.pop("final_overs_balls"))
                match.bonus_value = clean(row.pop("bonus_value"))
                match.bonus_applicable = clean(row.pop("bonus_applicable"))
                match.winning_score = clean(row.pop("winning_score"))
                match.calculated_winning_score = clean(
                    row.pop("calculated_winning_score")
                )
                match.final_winning_score = clean(row.pop("final_winning_score"))
                match.bat_first_team = Squad.objects.get(
                    id=clean(row.pop("bat_first_team"))
                )
                match.winning_team = Squad.objects.get(
                    id=clean(row.pop("winning_team"))
                )
                match.super_over_played = clean(row.pop("super_over_played"))

                match.dl_applicable = clean(row.pop("dl_applicable"))
                match.dl_overs = clean(row.pop("dl_overs"))
                match.dl_overs_balls = clean(row.pop("dl_overs_balls"))
                match.dl_target = clean(row.pop("dl_target"))

                s_o_w = row.pop("super_over_winner")
                if s_o_w is not None and s_o_w != "":
                    match.super_over_winner = Squad.objects.get(id=int(s_o_w))

                match.win_margin_runs = clean(row.pop("win_margin_runs"))
                match.first_wicket_gone_in_over = clean(
                    row.pop("first_wicket_gone_in_over")
                )

                match.save()

            fil.close()

        except Exception as exp:
            raise CommandError(exp)

        else:
            self.stdout.write("Loaded {} from: {}".format("MATCH DETAILS", csv_file))
            self.stdout.write("New match ID is: {}".format(match.id))

    @transaction.atomic
    def import_performance(self, performance_type, klass, csv_file, match_id):
        try:
            fil = open(csv_file)
            reader = csv.DictReader(fil)
            match = Match.objects.get(id=match_id)
            test_obj = klass()
            count = 0
            for row in reader:
                klass_obj = klass()
                name = row.pop("player").strip()
                print("Importing stats for: {}".format(name))
                p = Player.objects.filter(name=name)[0]
                klass_obj.player = p
                klass_obj.match = match
                bowlers = []
                fielders = []
                count = count + 1

                if isinstance(test_obj, BattingPerformance):

                    # set bowler
                    bowlers = parse_players(row.pop("bowler"))
                    if len(bowlers) == 1:
                        klass_obj.bowler = bowlers[0]

                    # get fielders, reserver for now
                    fielders = parse_players(row.pop("fielder"))

                for k, v in row.items():
                    value = clean(v)
                    # handle predefined constants within the class
                    if hasattr(klass_obj, v):
                        value = getattr(klass_obj, v)
                    setattr(klass_obj, k, value)

                # Add team
                klass_obj.team = klass_obj.player.team(klass_obj.match)
                klass_obj.save()

                # Add fielders now, as m-2-m needs an id before
                # value can be assigned
                if len(fielders) > 0:
                    for f in fielders:
                        klass_obj.fielder.add(f)
                klass_obj.save()

                # Populate attribute in Match from MatchPerformance
                # if required
                if isinstance(test_obj, MatchPerformance):
                    m = "\tCross-recording {} record for {} in Match {}"

                    if klass_obj.max_fours_hit:
                        match.max_fours_by.add(klass_obj.player)
                        print(m.format("max-4", klass_obj.player, match))

                    if klass_obj.max_sixes_hit:
                        match.max_sixes_by.add(klass_obj.player)
                        print(m.format("max-6", klass_obj.player, match))

                    if klass_obj.most_runs:
                        match.most_runs_by.add(klass_obj.player)
                        print(m.format("max-runs", klass_obj.player, match))

                    if klass_obj.most_wickets:
                        match.most_wickets_by.add(klass_obj.player)
                        print(m.format("max-wickets", klass_obj.player, match))

                    match.save()

            fil.close()

        except Exception as exp:
            raise exp

        else:
            self.stdout.write(
                "Loaded total of: {} {} performances from: {}".format(
                    count, performance_type.capitalize(), csv_file
                )
            )
