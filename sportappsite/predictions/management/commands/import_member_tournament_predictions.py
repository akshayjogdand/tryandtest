import csv
import uuid
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from fixtures.models import Player, Team, Tournament

from members.models import Member, MemberGroup, Membership

from predictions.models import MemberTournamentPrediction


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
    except:
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
    help = "Load Member Tournament Predictions from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tournament-id", type=int, help="Tournament ID", required=True
        )
        parser.add_argument(
            "--group-id", type=int, help="Group ID to load data against", required=True
        )
        parser.add_argument(
            "--csv-file", type=str, help="path to CSV file", required=True
        )

    @transaction.atomic
    def handle(self, tournament_id, group_id, csv_file, *args, **options):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            group = MemberGroup.objects.get(id=group_id)
        except MemberGroup.DoesNotExist:
            raise CommandError(
                "Member Group with ID={} does not exist".format(group_id)
            )
        except Tournament.DoesNotExist:
            raise CommandError(
                "Tournament with ID={} does not exist".format(tournament_id)
            )

        try:
            fil = open(csv_file)
            reader = csv.DictReader(fil)

            for row in reader:
                mp = MemberTournamentPrediction()
                mp.member_group = group
                mp.tournament = tournament
                mp.member = get_or_create_member(clean(row.pop("member")), group)

                for k, v in row.items():
                    if "_team" in k:
                        setattr(mp, k, get_team(clean(v)))

                    else:
                        setattr(mp, k, get_player(clean(v)))
                mp.save()

            fil.close()

        except Exception as exp:
            raise exp
        else:
            self.stdout.write("Loaded Member Tournament Predictions")
