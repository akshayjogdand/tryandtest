import csv
import datetime
import uuid
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from fixtures.models import Match, Player, Team

from members.models import Member, MemberGroup, Membership

from predictions.models import MemberPrediction


def get_team(team_id):
    if team_id == "" or team_id is None:
        return None
    else:
        return Team.objects.get(id=team_id)


def get_player(name):
    if name == "" or name is None:
        return None
    else:
        try:
            return Player.objects.filter(name=name)[0]
        except Exception as exp:
            print("Error fetching Player: {}".format(name))
            raise exp


def clean(value):
    v = value.strip()

    try:
        c = int(v)
    except ValueError:
        if v == "":
            return None
        else:
            return v
    else:
        return c


def check_or_add_membership(member, group):
    try:
        membership = Membership.objects.get(member=member, member_group=group)
    except Membership.DoesNotExist:
        membership = Membership()
        membership.member_group = group
        membership.member = member
        membership.save()


def get_or_create_member(member_name, group):
    fname, lname = member_name.split(" ")
    member = Member.objects.filter(
        user__first_name=fname, user__last_name=lname
    ).first()
    if member is None:
        member = Member()
        user = User()
        user.first_name = fname
        user.last_name = lname
        user.username = "{}_{}".format(fname.lower(), lname.lower())
        user.set_password(uuid.uuid4().hex[0 : random.randint(10, 32)])
        user.save()
        member.user = user
        member.save()

    check_or_add_membership(member, group)

    return member


class Command(BaseCommand):
    help = "Load Member Predictions from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("--match-id", type=int, help="Match ID", required=True)
        parser.add_argument(
            "--group-id", type=int, help="Group ID to load data against", required=True
        )
        parser.add_argument(
            "--csv-file", type=str, help="path to CSV file", required=True
        )

    @transaction.atomic
    def handle(self, match_id, group_id, csv_file, *args, **options):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            raise CommandError("Match with ID={} does not exist".format(match_id))

        try:
            group = MemberGroup.objects.get(id=group_id)
        except MemberGroup.DoesNotExist:
            raise CommandError(
                "Member Group with ID={} does not exist".format(group_id)
            )

        try:
            fil = open(csv_file)
            reader = csv.DictReader(fil)
            loaded = []
            for row in reader:
                mp = MemberPrediction()
                mp.match = match
                mp.member_group = group
                mp.member = get_or_create_member(clean(row.pop("member")), group)

                mp.predicted_winning_team = get_team(
                    clean(row.pop("predicted_winning_team"))
                )
                mp.predicted_winning_team_score = clean(
                    row.pop("predicted_winning_team_score")
                )
                mp.predicted_first_wicket_gone_in_over = clean(
                    row.pop("predicted_first_wicket_gone_in_over")
                )
                mp.predicted_win_margin_range = clean(
                    row.pop("predicted_win_margin_range")
                )

                mp.player_one = get_player(clean(row.pop("player_one")))
                mp.player_two = get_player(clean(row.pop("player_two")))
                mp.player_three = get_player(clean(row.pop("player_three")))
                mp.player_four = get_player(clean(row.pop("player_four")))
                mp.super_player = get_player(clean(row.pop("super_player")))
                mp.game_bonus = clean(row.pop("game_bonus"))
                sub_dt = clean(row.pop("submission_time"))

                mp.player_with_most_fours = get_player(
                    clean(row.pop("player_with_most_fours"))
                )
                mp.player_with_most_sixes = get_player(
                    clean(row.pop("player_with_most_sixes"))
                )
                mp.player_with_most_runs = get_player(
                    clean(row.pop("player_with_most_runs"))
                )
                mp.player_with_most_wickets = get_player(
                    clean(row.pop("player_with_most_wickets"))
                )

                mp.total_extras = clean(row.pop("total_extras"))
                mp.total_free_hits = clean(row.pop("total_free_hits"))
                mp.total_run_outs = clean(row.pop("total_run_outs"))
                mp.total_catches = clean(row.pop("total_catches"))
                mp.total_wickets = clean(row.pop("total_wickets"))
                mp.total_wides = clean(row.pop("total_wides"))
                mp.total_noballs = clean(row.pop("total_noballs"))
                mp.total_byes = clean(row.pop("total_byes"))
                mp.total_legbyes = clean(row.pop("total_legbyes"))
                mp.total_bowled = clean(row.pop("total_bowled"))
                mp.total_stumpings = clean(row.pop("total_stumpings"))
                mp.total_lbws = clean(row.pop("total_lbws"))
                mp.total_sixes = clean(row.pop("total_sixes"))
                mp.total_fours = clean(row.pop("total_fours"))
                mp.toss_winner = get_team(clean(row.pop("toss_winner")))

                t_o = clean(row.pop("toss_outcome"))
                if t_o is not None:
                    mp.toss_outcome = getattr(Match, t_o)

                t_d = clean(row.pop("toss_decision"))
                if t_d is not None:
                    mp.toss_decision = getattr(Match, t_d)

                if sub_dt is not None:
                    mp.submision_time = datetime.datetime.strptime(
                        sub_dt, "%d/%m/%Y %H:%M"
                    )
                else:
                    mp.submision_time = None

                mp.save()
                loaded.append(mp)

            fil.close()

        except Exception as exp:
            raise exp
        else:
            print("Loaded member predictions:")
            for i, mp in enumerate(loaded, 1):
                print("{}, {}".format(i, mp))
