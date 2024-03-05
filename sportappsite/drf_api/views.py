from collections import defaultdict

from django.db import transaction
from django.db.models import Model as DjangoModel
from django.db.models import Avg, Q
from django.utils import timezone
from django.middleware import csrf

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import serializers

from members.models import (
    GroupLeaderBoard,
    LeaderBoardEntry,
    Member,
    MemberGroup,
    Membership,
    MemberGroupInvitation,
)

from members.models import (
    create_member_group_from_spare,
    MemberGroupExists,
    MemberGroupRules,
    member_exists,
    create_member,
    accept_invite,
    add_to_default_member_group,
)

from members.utils import (
    reset_member_password,
    member_memberships,
    has_membership,
    has_active_membership,
    verify_member_email,
    set_member_email_as_verfied,
    resolve_member,
)


from app_media.utils import get_media

from app_media.models import AppMedia

from members.emails import send_invite_email, send_contact_email

from predictions.models import (
    MemberPrediction,
    GroupSubmissionsConfig,
    MemberSubmission,
    MemberSubmissionData,
    MemberTournamentPrediction,
    SubmissionFieldConfig,
)
from predictions import stats

from predictions.scoring import apply_submission_validation_rules

from fixtures.models import Match, Tournament, PlayerTournamentHistory

from configurations.models import ConfigItem

from rules.models import Rule, R1

from stats.models import PlayerStat, TeamStat, PredictionFieldStat

from DynamicContent.models import MessageBlock

from securities.utils import is_access_allowed, clear_access_attempts, verify_captcha

from rewards.models import (
    TournamentReward,
    TournamentRewardParticipant,
    TournamentRewardAgreement,
)

from .serializers import (
    GroupLeaderBoardSerializer,
    LeaderBoardEntrySerializer,
    MemberGroupSerializer,
    RegisterMemberSerializer,
    GroupMatchSubmissionsConfigSerializer,
    SubmitMatchPredictionSerializer,
    MemberSubmissionSerializer,
    MatchSerializer,
    GroupTournamentSubmissionsConfigSerializer,
    SubmitTournamentPredictionSerializer,
    RegisterMemberGroupSerializer,
    MemberGroupInvitations,
    TeamSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    PlayerStatSerializer,
    ContactFormSerializer,
    MessageBlockSerializer,
    JoinMemberGroupSerializer,
    AppMediaSerializer,
    TournamentRewardSerializer,
    SubmitTournamentRewardSerializer,
    PlayerSerializer,
    TeamSerializer,
    MemberGroupOnlySerializer,
    MemberSerializer,
    UserSerializer,
    MemberProfileSerializer,
    GroupTournamentSubmissionsConfigDetailsSerializer,
    MemberSubmissionWithColumnOrderingSerializer,
    MemberTouramentPredictionWithColumnOrderingSerializer,
    MemberPredictionWithColumnOrderingSerializer,
    MemberPredictionScoreWithColumnOrderingSerializer,
    PredictionStatSerializer,
    MemberSerializer,
    MemberPredictionScoreWithColumnOrderingSerializer,
    MemberGroupNameSerializer,
    TournamentSerializer,
)

from rest_framework_jwt.views import ObtainJSONWebToken

from .schedules import crosspost_async

import logging

logger = logging.getLogger("django")


def parse_boolean(some_str):
    return some_str == "True"


# TODO check each object actually belongs to the related match.team,
# tournament.match, as well as if allowed for particular groups, etc
def check_submission_fields_and_data(
    raw_submission_data, member_group, tournament, submission_type, tournament_format
):
    errors = {}
    messages = []
    submission_values = {}

    config = GroupSubmissionsConfig.objects.get(
        member_group=member_group,
        tournament=tournament,
        submission_type=(submission_type),
        tournament_format=tournament_format,
    )

    allowed_fields = config.submission_fields.all()
    allowed_field_ids = [f.field for f in allowed_fields]

    for field_id, raw_field_value in raw_submission_data.items():
        if field_id not in allowed_field_ids:
            messages.append(
                "Submission Field with ID: {field_id} is not allowed.".format(
                    field_id=field_id
                )
            )

        for f in allowed_fields:
            if field_id == f.field:
                field_config = f
                break

        field_type = field_config.get_model_type()
        value_object = None

        if isinstance(field_type, DjangoModel):
            value_object = field_type.objects.get(id=int(raw_field_value))
        else:
            try:
                value_object = field_type(raw_field_value)
            except ValueError:
                messages.append(
                    "'{}' is not an acceptable value.".format(raw_field_value)
                )

        submission_values[field_config.FIELDS.get(field_id)] = (
            field_type,
            value_object,
        )

    if len(messages) > 0:
        errors["submisison_data"] = messages

    return submission_values, errors


def check_submission(serializer, user, submission_type):
    errors = dict()
    xpost = match = tournament = member_group = member = submission_data = None

    try:
        xpost = serializer["crosspost"].value
        tournament = Tournament.objects.get(id=serializer.data["tournament"])
        member_group = MemberGroup.objects.get(id=serializer.data["member_group"])
        member, memberships = member_memberships(user)

        if submission_type == GroupSubmissionsConfig.MATCH_DATA_SUBMISSION:
            match = Match.objects.get(id=serializer.data["match"])
        else:
            match = None

    except Match.DoesNotExist:
        errors["match"] = ["Match with given ID does not exist."]

    except Tournament.DoesNotExist:
        errors["tournament"] = ["Tourament with given ID does not exist."]

    except MemberGroup.DoesNotExist:
        errors["member_group"] = ["Member Group with given ID does not exist."]

    if member_group and not has_membership(memberships, member_group):
        errors["memberships"] = ["Member is not part of Member Group."]

    if match and not match.submissions_allowed:
        if not match.post_toss_changes_allowed:
            errors["match"] = ["No Prediction allowed for given Match."]

    submission_data = serializer.data["submission_data"]
    if len(submission_data) == 0:
        errors["submission_data"] = ["No Prediction field data has been submit."]

    if not all([k.isnumeric() for k in submission_data.keys()]):
        errors["submission_data"] = ["Invalid Field ID in submisison_data."]
    else:
        submission_data = {int(k): v for k, v in submission_data.items()}

    return errors, xpost, match, tournament, member, member_group, submission_data


@transaction.atomic
def create_submission(serializer, user, submission_type):
    (
        errors,
        xpost,
        match,
        tournament,
        member,
        member_group,
        raw_submission_data,
    ) = check_submission(serializer, user, submission_type)

    if len(errors) > 0:
        # TODO this needs logging.
        return errors

    tournament_format = serializer.data.get("tournament_format", None)

    if not tournament_format:
        tournament_format = match.match_type

    (resolved_submission_values, field_errors) = check_submission_fields_and_data(
        raw_submission_data,
        member_group,
        tournament,
        submission_type,
        tournament_format,
    )

    if len(field_errors) > 0:
        return field_errors

    member_submission = MemberSubmission()
    member_submission.member = member
    member_submission.member_group = member_group
    member_submission.match = match
    member_submission.tournament = tournament
    member_submission.is_valid = True
    member_submission.submission_type = submission_type
    member_submission.submission_format = tournament_format
    member_submission.request_time = timezone.now()

    if match:
        member_submission.is_post_toss = match.post_toss_changes_allowed
    member_submission.save()

    for field_name, (field_type, field_value) in resolved_submission_values.items():
        sd = MemberSubmissionData()
        sd.member_submission = member_submission
        sd.field_name = field_name
        sd.set_value(field_type, field_value)
        sd.save()

    rule_errors = apply_submission_validation_rules(
        member_submission, submission_type, tournament_format
    )

    if len(rule_errors) > 0:
        member_submission.is_valid = False
        member_submission.validation_errors = "\n\n".join(rule_errors)
        member_submission.save()
        return rule_errors

    if xpost:
        crosspost_async(
            user,
            member_group,
            match,
            tournament,
            member_submission,
            resolved_submission_values,
        )


def extract_from_request(request, *args):
    values = []
    source = request.data
    if len(request.data) == 0:
        source = request.query_params

    for var in args:
        value = source.get(var, None)
        if value:
            value = value.strip()
        values.append(value)

    if len(values) == 1:
        return values[0]
    else:
        return values


@transaction.atomic
def create_invitations(member, member_group, invitations):
    for invite in invitations:
        if not MemberGroupInvitation.objects.filter(
            invited_email=invite["email"], member_group=member_group
        ).exists():
            mi = MemberGroupInvitation()
            mi.inviter = member
            mi.member_group = member_group
            mi.invited_name = invite["name"]
            mi.invited_email = invite["email"]
            mi.invitation_code = member_group.invitation_code
            mi.save()

            invited_member = member_exists(mi.invited_email)
            if invited_member:
                existing_member, memberships = member_memberships(invited_member.user)
                if not has_membership(memberships, member_group):
                    accept_invite(invited_member, mi)
            else:
                send_invite_email(mi)


class PredictionScoringRulesView(APIView):
    allowed_methods = ("GET",)

    def get(self, request):
        member, memberships = member_memberships(request.user)
        match_format = int(extract_from_request(request, "match_format"))
        rules = []

        for m in memberships:
            try:
                mgr = MemberGroupRules.objects.get(member_group=m.member_group)
                group_rules = mgr.group_prediction_scoring_rules
                rules.extend(
                    [
                        o
                        for o in group_rules.all()
                        if o.is_enabled
                        and o.rule_category != Rule.CAT_NOT_SET
                        and o.apply_to_match_type == match_format
                    ]
                )
            except MemberGroupRules.DoesNotExist:
                pass

        rule_set = set([r.parent_rule for r in rules])
        data = dict()

        for r in rule_set:
            category = r.category_name()
            if category in data:
                data[category].append(
                    {
                        "rule_name": r.name,
                        "description": r.description,
                        "points": r.points_or_factor,
                        "display_order": r.display_order,
                    }
                )
            else:
                data[category] = list()
                data[category].append(
                    {
                        "rule_name": r.name,
                        "description": r.description,
                        "points": r.points_or_factor,
                        "display_order": r.display_order,
                    }
                )

        cat_rules = []
        for cat, r_list in data.items():
            r_list.sort(key=lambda r: r["display_order"])
            cat_rules.append({"category": cat, "rules": r_list})

        return Response(cat_rules, status.HTTP_200_OK)


class PlayerScoringRulesView(APIView):
    allowed_methods = ("GET",)

    def get(self, request):
        member, memberships = member_memberships(request.user)
        match_format = int(extract_from_request(request, "match_format"))
        rules = []

        for m in memberships:
            try:
                mgr = MemberGroupRules.objects.get(member_group=m.member_group)
                group_rules = mgr.group_player_scoring_rules
                rules.extend(
                    [
                        o
                        for o in group_rules.all()
                        if o.is_enabled
                        and o.rule_category != Rule.CAT_NOT_SET
                        and o.apply_to_match_type == match_format
                    ]
                )
            except:
                pass

        rule_set = set([r.parent_rule for r in rules])
        data = dict()

        for r in rule_set:
            category = r.category_name()
            if not category in data:
                data[category] = list()

            ranges = []
            r1s = R1.objects.filter(rule=r.id)
            for r1 in r1s:
                ranges.append(
                    {"description": r1.range_description, "points": r1.points,}
                )

            data[category].append(
                {
                    "rule_name": r.name,
                    "description": r.description,
                    "points": r.points_or_factor,
                    "display_order": r.display_order,
                    "ranges": ranges,
                }
            )

        cat_rules = []
        for cat, r_list in data.items():
            r_list.sort(key=lambda r: r["display_order"])
            cat_rules.append({"category": cat, "rules": r_list})

        return Response(cat_rules, status.HTTP_200_OK)


class MyTournamentsView(APIView):
    allowed_methods = ("GET",)

    def get(self, request):
        member, memberships = member_memberships(request.user)
        tournaments = []

        for m in memberships:
            for t in m.member_group.tournaments.all():
                tournaments.append(
                    {
                        "id": t.id,
                        "name": t.name,
                        "abbreviation": t.abbreviation,
                        "start_date": t.start_date,
                        "media": AppMediaSerializer(t.media.all(), many=True).data,
                        "odi_series": t.odi_series,
                        "t20_series": t.t20_series,
                        "test_series": t.test_series,
                        "is_active": t.is_active,
                    }
                )

        t_set = {t["id"]: t for t in tournaments}.values()

        t_set = [t for t in t_set]

        def sortSecond(val):
            return val["start_date"].timestamp()

        t_set.sort(key=sortSecond, reverse=True)

        return Response(t_set, status.HTTP_200_OK)


class GroupsTournamentsView(APIView):
    allowed_methods = ("GET",)

    def get(self, request):
        # in past tournament we need only in active tournament
        # in past match we need all tournaments
        # for_past = match/tournament default tournament
        for_past = extract_from_request(request, "for_past")
        member, memberships = member_memberships(request.user, True)
        data = []
        for m in memberships:
            member_group = m.member_group
            tournaments = []

            # if true get all tournaments
            # if false get only tournament which start date is less then inactive date
            ts = []
            if m.active:
                ts = member_group.tournaments.all()
            else:
                ts = member_group.tournaments.filter(start_date__lt=m.marked_inactive)

            if for_past == "match":
                ms = Match.objects.filter(
                    tournament_id__in=ts,
                    match_status__in=[Match.COMPLETED, Match.LIVE],
                    fake_match=False,
                )
                mts = [m.tournament_id for m in ms]
                ts = ts.filter(id__in=mts).order_by("-end_date")
            else:
                ts = ts.order_by("-end_date")

            for t in ts:
                tournaments.append(
                    {
                        "id": t.id,
                        "name": t.name,
                        "is_active": t.is_active,
                        "abbreviation": t.abbreviation,
                        "media": AppMediaSerializer(t.media.all(), many=True).data,
                    }
                )

            mg = {
                "id": member_group.id,
                "name": member_group.name(),
                "tournaments": tournaments,
            }

            if len(tournaments) > 0:
                data.append(mg)

        return Response(data, status.HTTP_200_OK)


class TournamentTeamView(ListAPIView):
    allowed_methods = ("GET",)
    serializer_class = TeamSerializer

    def get_queryset(self):
        tournament_id = extract_from_request(self.request, "tournament")
        tournament = Tournament.objects.get(id=tournament_id)

        return set(
            [
                th.team
                for th in PlayerTournamentHistory.objects.filter(tournament=tournament)
            ]
        )


class TeamPlayersView(APIView):
    allowed_methods = ("GET",)

    def player_json(self, tph):
        return {
            "id": tph.player.id,
            "name": tph.player.name,
            "jersey_number": tph.jersey_number,
            "player_hand": tph.player.hand(),
            "player_skill": tph.player.skill(),
            "player_media": AppMediaSerializer(tph.player.media.all(), many=True).data,
        }

    def get(self, request):
        tournament_id, tournament_format = extract_from_request(
            request, "tournament", "tournament_format"
        )
        tournament = Tournament.objects.get(id=tournament_id)
        tournament_format = int(tournament_format)
        data = []

        teams = set(
            th.team
            for th in PlayerTournamentHistory.objects.filter(tournament=tournament)
        )

        teams = sorted(teams, key=lambda t: t.name)

        for team in teams:
            td = {
                "team_id": team.id,
                "name": team.name,
                "media": AppMediaSerializer(team.media.all(), many=True).data,
            }
            batsmen = []
            bowlers = []
            wicket_keepers = []
            all_rounders = []
            all_players = []

            players_tph = (
                PlayerTournamentHistory.objects.filter(
                    tournament=tournament, team=team,
                )
                .order_by("player__name")
                .exclude(status=PlayerTournamentHistory.PLAYER_WITHDRAWN)
                .all()
            )

            for t in players_tph:
                # filter player based on series
                if not (
                    (t.t20_player == True and tournament_format == Match.T_TWENTY)
                    or (t.odi_player == True and tournament_format == Match.ONE_DAY)
                    or (t.test_player == True and tournament_format == Match.TEST)
                ):
                    continue

                all_players.append(self.player_json(t))

                if t.player_skill == PlayerTournamentHistory.BOWLER:
                    bowlers.append(self.player_json(t))

                elif t.player_skill == PlayerTournamentHistory.BATSMAN:
                    batsmen.append(self.player_json(t))

                elif t.player_skill == PlayerTournamentHistory.ALLROUNDER:
                    all_rounders.append(self.player_json(t))

                elif t.player_skill == PlayerTournamentHistory.KEEPER:
                    wicket_keepers.append(self.player_json(t))

                if tournament_format == Match.TEST:
                    if t.test_captain:
                        td["captain"] = self.player_json(t)

                    if t.test_vice_captain:
                        td["vice_captain"] = self.player_json(t)

                if tournament_format == Match.ONE_DAY:
                    if t.odi_captain:
                        td["captain"] = self.player_json(t)

                    if t.odi_vice_captain:
                        td["vice_captain"] = self.player_json(t)

                if tournament_format == Match.T_TWENTY:
                    if t.t20_captain:
                        td["captain"] = self.player_json(t)

                    if t.t20_vice_captain:
                        td["vice_captain"] = self.player_json(t)

            td["batsmen"] = batsmen
            td["bowlers"] = bowlers
            td["wicket_keepers"] = wicket_keepers
            td["all_rounders"] = all_rounders
            td["all_players"] = all_players
            data.append(td)

        return Response(data, status.HTTP_200_OK)


class GroupPastMatchesView(ListAPIView):
    allowed_methods = ("GET",)
    serializer_class = MatchSerializer

    def get_queryset(self):
        member, memberships = member_memberships(self.request.user, True)
        group_id = int(extract_from_request(self.request, "member_group"))
        member_group = MemberGroup.objects.get(id=group_id)
        tournament_id = extract_from_request(self.request, "tournament")

        filters = {
            "match_status__in": (Match.COMPLETED, Match.LIVE),
            "fake_match": False,
        }

        if tournament_id:
            tournament = Tournament.objects.get(id=tournament_id)
            filters["tournament"] = tournament
        else:
            filters["tournament__in"] = member_group.tournaments.all()

        current_group_membership = None
        for m in memberships:
            if member_group.id == m.member_group_id:
                current_group_membership = m

        if current_group_membership is not None:
            if not current_group_membership.active:
                filters["match_date__lt"] = current_group_membership.marked_inactive
            return Match.objects.filter(**filters).order_by("-match_date").all()


class GroupAllowedMatchesView(APIView):
    allowed_methods = ("GET",)

    def get(self, request):
        member, memberships = member_memberships(self.request.user)
        data = []

        for m in memberships:
            tournament_ids = []
            tournaments = (
                m.member_group.tournaments.filter(is_active=True)
                .order_by("start_date")
                .all()
            )
            matches = Match.objects.filter(
                Q(submissions_allowed=True) | Q(post_toss_changes_allowed=True),
                tournament__in=tournaments,
            ).order_by("match_date")

            if matches.count() > 0:
                match_list = []
                for match in matches:
                    tournament_ids.append(match.tournament_id)
                    match_list.append(
                        {
                            "id": match.id,
                            "tournament_id": match.tournament_id,
                            "match_number": match.match_number,
                            "match_type": match.match_type,
                            "toss_time": match.toss_time,
                            "local_start_time": match.local_start_time(),
                            "start_time_utc": match.start_time_utc(),
                            "short_display_name": match.short_display_name,
                            "teams": TeamSerializer(match.teams(), many=True).data,
                            "submission_status": match.submission_status(),
                        }
                    )
                data.append(
                    {
                        "member_group_id": m.member_group.id,
                        "member_group_name": m.member_group.name(),
                        "tournaments": TournamentSerializer(
                            tournaments.filter(id__in=tournament_ids), many=True
                        ).data,
                        "matches": match_list,
                    }
                )

        return Response(data, status.HTTP_200_OK)


class MemberPredictionsView(ListAPIView):
    serializer_class = MemberPredictionWithColumnOrderingSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        member, memberships = member_memberships(self.request.user, True)
        tournament_id, match_id, group_id, member_id = extract_from_request(
            self.request, "tournament", "match", "member_group", "member"
        )
        filter_by = {}

        # Member Group is mandatory
        member_group = MemberGroup.objects.get(id=group_id)
        member_group_membership = None
        for m in memberships:
            if m.member_group_id == int(group_id):
                member_group_membership = m
                break

        if member_group_membership is None:
            # TODO log this
            return

        # Filter by logged in Member by default
        filter_by["member_id"] = member.id
        filter_by["match__fake_match"] = False

        if member_id:
            if member_id.isnumeric():
                filter_by["member_id"] = member_id
            elif not member_id.isnumeric() and member_id.lower() == "all":
                filter_by.pop("member_id")
                if member_group_membership.active is False:
                    filter_by["member__in"] = member_group.members.filter(
                        Q(
                            membership__date_joined__lte=member_group_membership.marked_inactive
                        )
                        | Q(id=member_group_membership.member_id)
                    )
            else:
                pass

        if tournament_id:
            filter_by["match__tournament"] = Tournament.objects.get(id=tournament_id)

        if match_id:
            if match_id.isnumeric():
                filter_by["match"] = Match.objects.get(id=match_id)
            elif not match_id.isnumeric() and match_id.lower() == "all":
                filter_by["match__match_status__in"] = [Match.COMPLETED, Match.LIVE]
                if member_group_membership.active is False:
                    filter_by[
                        "match__match_date__lte"
                    ] = member_group_membership.marked_inactive
            elif not match_id.isnumeric() and match_id.lower() != "all":
                pass

        # Need at least Member or Match or Tournament
        if len(filter_by) == 0:
            return

        results = MemberPrediction.objects.filter(
            member_group=member_group, **filter_by
        ).order_by("-match__match_number")

        column_ordering = []
        if len(results) > 0:
            column_ordering = results[0].table_column_ordering()

        ms = {"data": results, "table_column_ordering": column_ordering}
        return [ms]


class MemberTournamentPredictionsView(ListAPIView):
    serializer_class = MemberTouramentPredictionWithColumnOrderingSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        member, memberships = member_memberships(self.request.user, True)
        tournament_id, group_id, member_id = extract_from_request(
            self.request, "tournament", "member_group", "member"
        )
        filter_by = {}

        # Member Group is mandatory
        member_group = MemberGroup.objects.get(id=group_id)
        member_group_membership = None
        for m in memberships:
            if m.member_group_id == int(group_id):
                member_group_membership = m
                break

        if member_group_membership is None:
            # TODO log this
            return

        # Filter by logged in Member by default
        filter_by["member_id"] = member.id
        if member_id:
            if member_id.isnumeric():
                filter_by["member_id"] = member_id
            elif not member_id.isnumeric() and member_id.lower() == "all":
                filter_by.pop("member_id")
                if member_group_membership.active is False:
                    filter_by["member__in"] = member_group.members.filter(
                        Q(
                            membership__date_joined__lte=member_group_membership.marked_inactive
                        )
                        | Q(id=member_group_membership.member_id)
                    )
            else:
                pass

        if tournament_id and tournament_id.isnumeric():
            filter_by["tournament"] = Tournament.objects.get(id=tournament_id)

        # Need at least Member or Match or Tournament
        if len(filter_by) == 0:
            return

        results = MemberTournamentPrediction.objects.filter(
            member_group=member_group, **filter_by
        )

        column_ordering = []
        if len(results) > 0:
            column_ordering = results[0].table_column_ordering()

        ms = {"data": results, "table_column_ordering": column_ordering}
        return [ms]


class SingleGroupLeaderBoard(ListAPIView):
    serializer_class = GroupLeaderBoardSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        member, memberships = member_memberships(self.request.user)
        board_id = extract_from_request(self.request, "board")
        board = GroupLeaderBoard.objects.get(id=board_id)
        member_group = board.member_group
        tournament = board.match.tournament
        data = []

        if has_membership(memberships, member_group):
            if tournament in member_group.tournaments.all():
                data.append(board)

        return data


class GroupLeaderBoardsView(ListAPIView):
    serializer_class = GroupLeaderBoardSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        tournament_active = parse_boolean(
            extract_from_request(self.request, "tournament_active")
        )
        member = {}
        memberships = []
        if tournament_active:
            member, memberships = member_memberships(self.request.user)
        else:
            member, memberships = member_memberships(self.request.user, True)

        boards = []
        for m in memberships:
            try:
                if m.active:
                    lb = GroupLeaderBoard.objects.filter(
                        member_group=m.member_group,
                        match__tournament__is_active=tournament_active,
                    ).latest("id")
                else:
                    lb = GroupLeaderBoard.objects.filter(
                        member_group=m.member_group,
                        match__tournament__is_active=tournament_active,
                        match__tournament__start_date__lt=m.marked_inactive,
                        match__match_date__lt=m.marked_inactive,
                    ).latest("id")
            except GroupLeaderBoard.DoesNotExist:
                continue
            else:
                boards.append(lb)

        def sortSecond(val):
            return val.computed_on.timestamp()

        boards.sort(key=sortSecond, reverse=True)

        return boards


class GroupsView(ListAPIView):
    serializer_class = MemberGroupSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        group_id = extract_from_request(self.request, "id")
        if group_id:
            group_id = int(group_id)

        member, memberships = member_memberships(self.request.user)

        if memberships:
            return [
                m.member_group
                for m in memberships
                if group_id is None or group_id == m.member_group.id
            ]


class GroupDetailsView(APIView):
    allowed_methods = ("GET",)

    def get(self, request):
        member_group_id = int(extract_from_request(request, "id"))
        add_inactive_members = parse_boolean(
            extract_from_request(request, "add_inactive_members")
        )
        member_group = None
        memberships = []
        members = []
        membership = None  # logged in user's membership

        try:
            member_group = MemberGroup.objects.get(id=member_group_id)
        except MemberGroup.DoesNotExist:
            return Response(
                {"non_field_errors": ["Member Group is not available."]},
                status.HTTP_400_BAD_REQUEST,
            )

        # find logged in user in member
        memberships = Membership.objects.filter(member_group_id=member_group_id)
        for m in memberships:
            if m.member.user_id == request.user.id:
                membership = m

        if membership is None:
            return Response(
                {"non_field_errors": ["You are not a member of this group."]},
                status.HTTP_400_BAD_REQUEST,
            )

        # check member status if inactive then filter others member
        if membership.active is not True:
            members = member_group.members.filter(
                Q(membership__date_joined__lte=membership.marked_inactive)
                | Q(id=membership.member_id)
            )
        else:
            if add_inactive_members is False:
                members = member_group.members.filter(membership__active=True)
            else:
                members = member_group.members.all()

        mg = MemberGroupOnlySerializer(member_group).data
        mg["members"] = MemberSerializer(members, many=True).data

        return Response(mg, status.HTTP_200_OK)


class LeaderBoardEntryView(ListAPIView):
    queryset = LeaderBoardEntry.objects.all()
    serializer_class = LeaderBoardEntrySerializer


class InviteMembersView(APIView):
    allowed_methods = ("POST",)

    def post(self, request, format=None):
        serializer = MemberGroupInvitations(data=request.data)
        member, memberships = member_memberships(request.user)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            member_group_id = extract_from_request(request, "member_group")
            member_group = MemberGroup.objects.get(id=member_group_id)

            if not has_membership(memberships, member_group):
                return Response(
                    {"non_field_errors": ["Not allowed to invite here."]},
                    status.HTTP_400_BAD_REQUEST,
                )
            else:
                create_invitations(member, member_group, serializer.data["invites"])
                return Response([], status.HTTP_201_CREATED)


class RegisterMemberGroupView(APIView):
    allowed_methods = ("POST",)

    def post(self, request, format=None):
        serializer = RegisterMemberGroupSerializer(data=request.data)
        member, _ = member_memberships(request.user)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                # getting membership after group created
                m = create_member_group_from_spare(
                    member, serializer.data["member_group_name"]
                )
                return Response(
                    MemberGroupSerializer(m, context={"request": request}).data,
                    status.HTTP_201_CREATED,
                )
            except MemberGroupExists as e:
                return Response(
                    {
                        "non_field_errors": [
                            "The username is taken. Please register with a different username."
                        ]
                    },
                    status.HTTP_400_BAD_REQUEST,
                )


class RegisterMemberView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ("POST",)

    def post(self, request, format=None):
        # verify captcha
        captcha_key, captcha_value = extract_from_request(
            self.request, "captcha_key", "captcha_value"
        )
        if verify_captcha(captcha_key, captcha_value) is False:
            return Response(
                {"non_field_errors": ["Invalid CAPTCHA, please try again."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # process register
        serializer = RegisterMemberSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # TODO move this checking to handling exceptions
            if member_exists(serializer.data["email"]):
                return Response(
                    {
                        "non_field_errors": [
                            "Sorry, we already have a Member with that email. Please try another one."
                        ]
                    },
                    status.HTTP_400_BAD_REQUEST,
                )

            else:
                try:
                    member = create_member(
                        serializer.data["email"],
                        serializer.data["first_name"],
                        serializer.data["last_name"],
                        serializer.data["password"],
                        serializer.data.get("invitation_code", None),
                    )
                except MemberGroup.DoesNotExist:
                    return Response(
                        {"non_field_errors": ["Invalid invitation code."]},
                        status.HTTP_400_BAD_REQUEST,
                    )

                verify_member_email(member)

        return Response([], status.HTTP_201_CREATED)


class AllowedMatchSubmissionsView(ListAPIView):
    allowed_methods = ("GET",)
    serializer_class = GroupMatchSubmissionsConfigSerializer

    def get_queryset(self):
        member, memberships = member_memberships(self.request.user)
        member_group_id = extract_from_request(self.request, "member_group")
        match_id = extract_from_request(self.request, "match")
        match = Match.objects.get(id=match_id)
        member_group = MemberGroup.objects.get(id=member_group_id)

        if has_membership(memberships, member_group):
            return GroupSubmissionsConfig.objects.filter(
                member_group=member_group,
                tournament=match.tournament,
                submission_type=GroupSubmissionsConfig.MATCH_DATA_SUBMISSION,
                tournament_format=match.match_type,
            )


class UpcomingMatchesView(ListAPIView):
    serializer_class = MatchSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        member, memberships = member_memberships(self.request.user)

        if memberships:
            member_groups = [m.member_group for m in memberships]
            tournaments = []
            for m in member_groups:
                tournaments.extend(m.tournaments.filter(is_active=True).all())

            return Match.objects.filter(
                Q(submissions_allowed=True) | Q(post_toss_changes_allowed=True),
                tournament__in=tournaments,
            ).order_by("match_date", "match_number")


class AllowedTournamentSubmissionsView(ListAPIView):
    serializer_class = GroupTournamentSubmissionsConfigSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        member, memberships = member_memberships(self.request.user)

        if memberships:
            member_groups = [m.member_group for m in memberships]
            now = timezone.now()
            return GroupSubmissionsConfig.objects.filter(
                member_group__in=member_groups,
                submission_type=GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION,
                tournament__submissions_allowed=True,
                tournament__is_active=True,
                active_from__lte=now,
                active_to__gte=now,
            ).order_by("active_to")


class AllowedTournamentSubmissionsDetailsView(ListAPIView):
    serializer_class = GroupTournamentSubmissionsConfigDetailsSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        tournament_id, member_group_id, tournament_format = map(
            int,
            extract_from_request(
                self.request, "tournament", "member_group", "tournament_format"
            ),
        )
        member, memberships = member_memberships(self.request.user)

        if memberships:
            member_groups = [m.member_group_id for m in memberships]
            now = timezone.now()

            # check member is part of the group
            if member_group_id in member_groups:
                return GroupSubmissionsConfig.objects.filter(
                    member_group_id=member_group_id,
                    tournament_id=tournament_id,
                    tournament_format=tournament_format,
                    submission_type=GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION,
                    tournament__submissions_allowed=True,
                    active_from__lte=now,
                    active_to__gte=now,
                ).order_by("tournament__is_active")


class SubmitMatchPredictionView(APIView):
    allowed_methods = ("POST",)

    def post(self, request, format=None):
        serializer = SubmitMatchPredictionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        errors = create_submission(
            serializer, request.user, GroupSubmissionsConfig.MATCH_DATA_SUBMISSION
        )

        if errors:
            return Response(errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response([], status.HTTP_201_CREATED)


class SubmitTournamentPredictionView(APIView):
    allowed_methods = ("POST",)

    def post(self, request, format=None):
        serializer = SubmitTournamentPredictionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        errors = create_submission(
            serializer, request.user, GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION
        )

        if errors:
            return Response(errors, status.HTTP_400_BAD_REQUEST)
        else:
            return Response([], status.HTTP_201_CREATED)


class GroupMatchSubmissionsView(ListAPIView):
    serializer_class = MemberSubmissionWithColumnOrderingSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        match_id, member_group_id = map(
            int, extract_from_request(self.request, "match", "member_group")
        )
        required_data = extract_from_request(self.request, "data")
        member, memberships = member_memberships(self.request.user)
        results = []

        if member and memberships and member_group_id and match_id:
            if has_membership(memberships, member_group_id):
                filter_by = {
                    "match": match_id,
                    "member_group": member_group_id,
                    "is_valid": True,
                    "converted_to_prediction": False,
                    "submission_type": GroupSubmissionsConfig.MATCH_DATA_SUBMISSION,
                }

        # Latest submission for everybody who has submitted.
        if required_data and required_data.lower() == "all":
            # Apply base filter.
            for ms in MemberSubmission.objects.filter(**filter_by).distinct("member"):
                try:
                    results.append(
                        MemberSubmission.objects.filter(
                            member=ms.member, **filter_by
                        ).latest("submission_time")
                    )

                except MemberSubmission.DoesNotExist:
                    continue

        # Logged in Member's latest submission
        else:
            try:
                filter_by["member"] = member
                results = [MemberSubmission.objects.filter(**filter_by).latest("id")]

            except MemberSubmission.DoesNotExist:
                pass

        column_ordering = []
        if len(results) > 0:
            column_ordering = results[0].table_column_ordering()
            results = sorted(results, key=lambda m: m.submission_time, reverse=True)

        ms = {"data": results, "table_column_ordering": column_ordering}
        return [ms]


class GroupTournamentSubmissionsView(ListAPIView):
    serializer_class = MemberSubmissionWithColumnOrderingSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        tournament_id, member_group_id, tournament_format_id = map(
            int,
            extract_from_request(
                self.request, "tournament", "member_group", "tournament_format"
            ),
        )
        required_data = extract_from_request(self.request, "data")
        member, memberships = member_memberships(self.request.user)
        member_group = MemberGroup.objects.get(id=member_group_id)
        tournament = Tournament.objects.get(id=tournament_id)
        results = []

        if member and memberships and member_group and tournament:
            if has_membership(memberships, member_group):
                filter_by = {
                    "tournament": tournament,
                    "member_group": member_group,
                    "is_valid": True,
                    "member": member,
                    "submission_format": tournament_format_id,  # TODO use constants
                    "submission_type": GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION,
                }

                if required_data and required_data.lower() == "all":
                    for m in member_group.members.all():
                        filter_by["member"] = m
                        try:
                            results.append(
                                MemberSubmission.objects.filter(**filter_by).latest(
                                    "id"
                                )
                            )
                        except MemberSubmission.DoesNotExist:
                            continue
                else:
                    try:
                        results = [
                            MemberSubmission.objects.filter(**filter_by).latest("id")
                        ]
                    except MemberSubmission.DoesNotExist:
                        pass

        column_ordering = []
        if len(results) > 0:
            column_ordering = results[0].table_column_ordering()

        ms = {"data": results, "table_column_ordering": column_ordering}
        return [ms]


class LastMemberGroupMatchSubmissionView(ListAPIView):
    serializer_class = MemberSubmissionSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        match_id, member_group_id = map(
            int, extract_from_request(self.request, "match", "member_group")
        )
        member, memberships = member_memberships(self.request.user)
        member_group = MemberGroup.objects.get(id=member_group_id)
        match = Match.objects.get(id=match_id)

        ms = []

        if member and memberships and member_group and match:
            if has_membership(memberships, member_group):
                try:

                    # TODO
                    #
                    # This needs to change based on following logic:
                    #   1. If match is open, is_post_toss should be false.
                    #
                    #   2. If match is in post toss, is_post_toss should be true.
                    #   2.1 if no data, try with is_post_toss set to false i.e. (1)
                    #
                    #   This should only be implemented after UI bug described in
                    #   68780fb96f94 is fixed -- as it can only be properly tested then.
                    #
                    ms = [
                        MemberSubmission.objects.filter(
                            member_group=member_group,
                            member=member,
                            match=match,
                            is_valid=True,
                            submission_type=GroupSubmissionsConfig.MATCH_DATA_SUBMISSION,
                            converted_to_prediction=False,
                        ).latest("id")
                    ]
                except MemberSubmission.DoesNotExist:
                    pass

            return ms


class LastMemberGroupTournamentSubmissionView(ListAPIView):
    serializer_class = MemberSubmissionSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        tournament_id, member_group_id, tournament_format_id = map(
            int,
            extract_from_request(
                self.request, "tournament", "member_group", "tournament_format"
            ),
        )
        member, memberships = member_memberships(self.request.user)
        member_group = MemberGroup.objects.get(id=member_group_id)
        tournament = Tournament.objects.get(id=tournament_id)

        ms = []

        if member and memberships and member_group and tournament:
            if has_membership(memberships, member_group):
                try:
                    ms = [
                        MemberSubmission.objects.filter(
                            member_group=member_group,
                            member=member,
                            tournament=tournament,
                            is_valid=True,
                            submission_format=tournament_format_id,  # TODO use constants
                            submission_type=GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION,
                        ).latest("id")
                    ]
                except MemberSubmission.DoesNotExist:
                    pass

            return ms


class MemberPointsView(APIView):
    """
    This api returns points matchwise for a given member in a given
    group for a given tournament.
    Graph: member performance(points) matchwise
    Input: group_id & tournament_id
    Output: Json Array. Every Element has {match_number, this_match}
    """

    allowed_methods = ("GET",)

    def get(self, request):
        group_id, tournament_id = extract_from_request(
            request, "member_group", "tournament"
        )
        member, memberships = member_memberships(request.user, True)

        try:
            member_group = MemberGroup.objects.get(id=group_id)
            tournament = Tournament.objects.get(id=tournament_id)
        except MemberGroup.DoesNotExist:
            member_group = None
        except Tournament.DoesNotExist:
            tournament = None

        membership = None

        for m in memberships:

            if member_group.id == m.member_group_id:
                membership = m

        if membership is None:
            return Response(
                {"non_field_errors": ["You are not a member of this group"]},
                status.HTTP_400_BAD_REQUEST,
            )

        if member_group and tournament and has_membership(memberships, member_group):
            member_points = (
                LeaderBoardEntry.objects.filter(leader_board__member_group=member_group)
                .filter(member=member)
                .filter(
                    leader_board__match__tournament=tournament,
                    leader_board__match__fake_match=False,
                )
                .order_by("leader_board")
            )

            if not membership.active:
                member_points = member_points.filter(
                    leader_board__match__match_date__lte=membership.marked_inactive
                )

            stats = []
            for me in member_points:
                stats.append(
                    {
                        "match_number": me.leader_board.match.match_number,
                        "points": me.this_match,
                    }
                )

            return Response(stats, status.HTTP_200_OK)

        else:
            return Response([], status.HTTP_200_OK)


class CompareTotalPoints(APIView):
    """
    This api returns comparative info of total_points for a
    given member in a given group for a given tournament.
    Graph: member performance vs group average.
    Input: group_id & tournament_id
    Output: Json array. Every element has {match_number, total, total_avg}
    """

    def get(self, request):
        group_id, tournament_id = extract_from_request(
            request, "member_group", "tournament"
        )
        member, memberships = member_memberships(request.user, True)

        try:
            member_group = MemberGroup.objects.get(id=group_id)
            tournament = Tournament.objects.get(id=tournament_id)
        except MemberGroup.DoesNotExist:
            member_group = None
        except Tournament.DoesNotExist:
            tournament = None

        membership = None

        for m in memberships:
            if member_group.id == m.member_group_id:

                membership = m

        if membership is None:
            return Response(
                {"non_field_errors": ["You are not a member of this group"]},
                status.HTTP_400_BAD_REQUEST,
            )

        if member_group and tournament and has_membership(memberships, member_group):

            stats = []
            # Average total points of the group w.r.t match
            group_avg_matchwise = (
                LeaderBoardEntry.objects.values("leader_board__match__match_number")
                .filter(leader_board__member_group=member_group)
                .filter(
                    leader_board__match__tournament=tournament,
                    leader_board__match__fake_match=False,
                )
                .order_by("leader_board__match__match_number")
                .annotate(Avg("total"))
            )

            if not membership.active:
                group_avg_matchwise = group_avg_matchwise.filter(
                    leader_board__match__match_date__lte=membership.marked_inactive
                )

            # Member's points across matches in that group
            member_total = (
                LeaderBoardEntry.objects.filter(leader_board__member_group=member_group)
                .filter(member=member)
                .filter(leader_board__match__tournament=tournament)
                .order_by("leader_board__match__match_number")
            )

            if not membership.active:
                member_total = member_total.filter(
                    leader_board__match__match_date__lte=membership.marked_inactive
                )

            for mt, gam in zip(member_total, group_avg_matchwise):
                stats.append(
                    {
                        "match": mt.leader_board.match.match_number,
                        "total": mt.total,
                        "total_avg": gam["total__avg"],
                    }
                )

            return Response(stats, status.HTTP_200_OK)

        else:
            return Response([], status.HTTP_200_OK)


class UpdatePasswordView(APIView):
    permission_classes = (IsAuthenticated,)
    allowed_methods = ("POST",)

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response(
                    {
                        "old_password": [
                            "Your Current Password is incorrect. Try again."
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ("POST",)

    def post(self, request, *args, **kwargs):
        # verify captcha
        captcha_key, captcha_value = extract_from_request(
            self.request, "captcha_key", "captcha_value"
        )
        if verify_captcha(captcha_key, captcha_value) is False:
            return Response(
                {"non_field_errors": ["Invalid CAPTCHA, please try again."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # process reset password
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            reset_member_password(serializer.data.get("email"))
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactFormView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ("POST",)

    def post(self, request, *args, **kwargs):
        # verify captcha
        captcha_key, captcha_value = extract_from_request(
            self.request, "captcha_key", "captcha_value"
        )
        if verify_captcha(captcha_key, captcha_value) is False:
            return Response(
                {"non_field_errors": ["Invalid CAPTCHA, please try again."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # process contact
        serializer = ContactFormSerializer(data=request.data)

        if serializer.is_valid():
            send_contact_email(**serializer.data)
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TouramentScheduleView(APIView):
    allowed_methods = ("GET",)

    def get(self, request):
        tournament_id, tournament_format = extract_from_request(
            request, "tournament", "tournament_format"
        )
        tournament_format = int(tournament_format)
        data = []
        tournaments = Tournament.objects.filter(is_active=True)

        if tournament_id:
            tournaments = tournaments.filter(id=tournament_id)

        tournaments = tournaments.order_by("start_date").all()

        for t in tournaments:
            # render tournament scheduled as per tournament format
            if (
                (tournament_format == Match.ONE_DAY and t.odi_series != True)
                or (tournament_format == Match.T_TWENTY and t.t20_series != True)
                or (tournament_format == Match.TEST and t.test_series != True)
            ):
                continue

            matches = []
            t_matches = Match.objects.filter(tournament=t, fake_match=False).order_by(
                "match_date"
            )
            for m in t_matches:
                teams = []
                # filter match basis on tournament format
                if m.match_type != tournament_format:
                    continue

                try:
                    teams = TeamSerializer(m.teams(), many=True).data
                except (Exception):
                    pass

                matches.append(
                    {
                        "id": m.id,
                        "match_number": m.match_number,
                        "name": m.teams_only_name(),
                        "teams": teams,
                        "venue": str(m.venue),
                        "start_time_utc": m.start_time_utc(),
                        "local_start_time": m.local_start_time(),
                    }
                )

            data.append({"id": t.id, "name": t.name, "matches": matches})

        return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def match_prediction_notes_text(request):
    text = ConfigItem.objects.get(name="match_prediction_notes_text")
    return Response(text.value)


class PredictionScoreView(ListAPIView):
    serializer_class = MemberPredictionScoreWithColumnOrderingSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        member_id, member_group_id, match_id = extract_from_request(
            self.request, "member", "member_group", "match"
        )

        if not all((member_id, member_group_id, match_id)):
            # TODO log this
            return []

        try:
            match = Match.objects.get(id=match_id)
            member = Member.objects.get(id=member_id)
            member_group = MemberGroup.objects.get(id=member_group_id)
            membership = Membership.objects.get(
                member=member, member_group=member_group
            )
        except (
            Member.DoesNotExist,
            MemberGroup.DoesNotExist,
            Membership.DoesNotExist,
            Match.DoesNotExist,
        ):
            # TODO log this
            return []

        try:
            results = [
                MemberPrediction.objects.get(
                    match=match, member=member, member_group=member_group
                )
            ]
        except:
            # TODO log this
            results = []

        column_ordering = []
        if len(results) > 0:
            column_ordering = results[0].table_column_ordering()

        ms = {"data": results, "table_column_ordering": column_ordering}
        return [ms]


class TouramentPredictionScoresView(ListAPIView):
    serializer_class = MemberTouramentPredictionWithColumnOrderingSerializer
    allowed_methods = ("GET",)

    def get_queryset(self):
        member, memberships = member_memberships(self.request.user)
        (
            member_id,
            member_group_id,
            tournament_id,
            tournament_format,
        ) = extract_from_request(
            self.request, "member", "member_group", "tournament", "tournament_format"
        )

        if not all((member_id, member_group_id, tournament_id)):
            return []

        try:

            tournament = Tournament.objects.get(id=tournament_id)
            member = Member.objects.get(id=member_id)
            member_group = MemberGroup.objects.get(id=member_group_id)

        except (
            Member.DoesNotExist,
            MemberGroup.DoesNotExist,
            Membership.DoesNotExist,
            Tournament.DoesNotExist,
        ):
            # TODO log this
            return {}

        if has_membership(memberships, member_group):
            try:
                results = [
                    MemberTournamentPrediction.objects.get(
                        tournament=tournament,
                        member=member,
                        prediction_format=tournament_format,
                        member_group=member_group,
                    )
                ]
            except:
                results = []

        column_ordering = []
        if len(results) > 0:
            column_ordering = results[0].table_column_ordering()

        ms = {"data": results, "table_column_ordering": column_ordering}
        return [ms]


class TopScoringPlayersView(APIView):
    allowed_methods = ("GET",)

    def get(self, request):
        tournament_id = extract_from_request(request, "tournament")
        tournaments = tournament_id.split(",")
        player_stats = PlayerStat.objects.filter(
            tournament__in=tournaments,
            stat_name="top_scoring_players_in_past_matches",
            is_latest=True,
        ).order_by("stat_index")

        json = []
        matches = defaultdict(list)

        for ps in player_stats:
            matches[ps.match].append(ps)

        for match, m_stats in matches.items():
            players = []
            for s in m_stats:
                players.append(
                    {
                        "player": PlayerSerializer(s.player).data,
                        "score": s.stat_value,
                        "team": TeamSerializer(s.team).data,
                    }
                )
            m = {
                "name": match.name,
                "match_number": match.match_number,
                "match_type": match.match_type,
            }
            json.append(
                {
                    "match": m,
                    "teams": TeamSerializer(match.teams(), many=True).data,
                    "players": players,
                    "tournament_id": match.tournament.id,
                }
            )

        return Response(json, status.HTTP_200_OK)


class TopScoringPlayersInTournamentView(ListAPIView):
    allowed_methods = ("GET",)
    serializer_class = PlayerStatSerializer

    def get_queryset(self):
        tournament_id = extract_from_request(self.request, "tournament")
        tournaments = tournament_id.split(",")

        player_stats = PlayerStat.objects.filter(
            tournament__in=tournaments,
            stat_name="top_scoring_players_in_tournament",
            is_latest=True,
        ).order_by("tournament", "stat_index")

        return player_stats


@permission_classes([])
class MessageBlocksView(APIView):
    allowed_methods = ("GET",)

    def get(self, request):
        message_name = extract_from_request(self.request, "message_name")
        try:
            message = MessageBlock.objects.get(message_name=message_name)
            message = MessageBlockSerializer(message).data
        except:
            message = {}
        return Response(message, status.HTTP_200_OK)


class LoginView(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        username = extract_from_request(request, "username")

        # check attempts
        if is_access_allowed(request) is False:
            return Response(
                {
                    "non_field_errors": [
                        "Maximum attempts exceeded. Please try after some time."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # process login
        username = extract_from_request(request, "username")
        response = super(LoginView, self).post(request, *args, **kwargs)

        if response.status_code is status.HTTP_200_OK:
            # clear on success
            clear_access_attempts(request)
            member = Member.objects.get(user__username=username)

            # check is member verified
            if not member.email_verified:
                verify_member_email(member)
                return Response(
                    {
                        "email_verified": False,
                        "details": [
                            "Thanks for registering. Please check you email for a verification link from us."
                        ],
                    },
                    status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
                )

            # success
            return Response(
                {
                    "csrf_token": csrf.get_token(request),
                    "token": response.data.get("token"),
                    "data": MemberProfileSerializer(member).data,
                },
                status=response.status_code,
            )
        return response


class JoinMemberGroupView(APIView):
    allowed_methods = ("POST",)

    def post(self, request, format=None):
        serializer = JoinMemberGroupSerializer(data=request.data)
        member, memberships = member_memberships(request.user)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            invitation_code = extract_from_request(request, "invitation_code")
            try:
                member_group = MemberGroup.objects.get(invitation_code=invitation_code)
            except MemberGroup.DoesNotExist:
                return Response(
                    {"non_field_errors": ["Invalid invitation code."]},
                    status.HTTP_400_BAD_REQUEST,
                )

            if has_active_membership(memberships, member_group):
                return Response(
                    {"non_field_errors": ["Already a Member."]},
                    status.HTTP_400_BAD_REQUEST,
                )

            try:
                m = Membership.objects.get(member=member, member_group=member_group)
            except Membership.DoesNotExist:
                m = Membership()

            m.active = True
            m.marked_inactive = None
            m.member = member
            m.member_group = member_group
            m.save()
            return Response(
                MemberGroupNameSerializer(member_group).data, status.HTTP_201_CREATED,
            )


class RemoveMembershipFromGroupView(APIView):
    allowed_methods = ("POST",)

    def post(self, request):
        remove_member_id, member_group_id = extract_from_request(
            request, "remove_member", "member_group"
        )

        try:
            admin_member = Membership.objects.get(
                member__user=request.user, member_group=member_group_id
            )
            membership_to_remove = Membership.objects.get(
                member_id=remove_member_id,
                member_group=member_group_id,
                active=True,
                is_admin=False,
            )

        except Membership.DoesNotExist:
            return Response(
                {"non_field_errors": ["Operation not permitted."]},
                status.HTTP_400_BAD_REQUEST,
            )

        membership_to_remove.active = False
        membership_to_remove.marked_inactive = timezone.now()
        membership_to_remove.save()

        mbs = MemberGroup.objects.filter(
            members__id=remove_member_id, membership__active=True
        )

        # Add to Global group if no more Memberships for this Member
        if mbs.count() == 0:
            add_to_default_member_group(membership_to_remove.member)

        return Response([], status.HTTP_200_OK)


class AppMediaView(ListAPIView):
    allowed_methods = ("GET",)
    serializer_class = AppMediaSerializer

    def get_queryset(self):
        player_id, team_id, country_id, media_size = extract_from_request(
            self.request, "player", "team", "country", "media_size"
        )

        filter_by = {}

        if player_id:
            filter_by["player"] = player_id
        elif team_id:
            filter_by["team"] = team_id
        elif country_id:
            filter_by["country"] = country_id
        elif media_size:
            filter_by["media_size"] = media_size

        return get_media(filter_by, True)


class GroupRewardsView(ListAPIView):
    allowed_methods = ("GET",)
    serializer_class = TournamentRewardSerializer

    def get_queryset(self):
        member, memberships = member_memberships(self.request.user)
        member_group_id = extract_from_request(self.request, "member_group")
        mg = MemberGroup.objects.get(id=member_group_id)

        if has_membership(memberships, mg):
            return TournamentReward.objects.filter(member_group=mg)

        else:
            return []


class SubmitTournamentRewardView(APIView):
    allowed_methods = ("POST",)
    serializer_class = SubmitTournamentRewardSerializer

    def post(self, request):
        member, _ = member_memberships(request.user)
        serializer = SubmitTournamentRewardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        tr = TournamentReward.objects.get(id=serializer.data.get("tournament_reward"))
        mg = tr.member_group
        is_admin = Membership.objects.get(member=member, member_group=mg).is_admin

        if not is_admin or tr.activated:
            return Response(status.HTTP_401_UNAUTHORIZED)

        for trp in serializer.data.get("participants"):
            trp_obj = TournamentRewardParticipant.objects.get(id=trp["participant_id"])
            trp_obj.contributor = trp["contributor"]
            trp_obj.contribution_amount = trp["contribution_amount"]
            trp_obj.save()

        tr.reward_pool = serializer.data.get("reward_pool")
        tr.contribution_per_member = serializer.data.get("contribution_per_member")
        tr.save()

        tra = TournamentRewardAgreement()
        tra.reward = tr
        tra.admin_member = member
        tra.agreement_text = tr.agreement_text
        tra.rewards_calculations_text = tr.rewards_calculations_text
        tra.save()

        return Response(status.HTTP_200_OK)


class MemberVerify(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request, type, token):
        if type == "email":
            if set_member_email_as_verfied(token):
                return Response([], status.HTTP_200_OK)
        return Response(
            {"non_field_erros": ["Invalid url or token has expired"]},
            status.HTTP_400_BAD_REQUEST,
        )


class MemberVerifyResendMail(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        username = extract_from_request(request, "username")
        # check attempts
        if is_access_allowed(request) is False:
            return Response(
                {
                    "non_field_errors": [
                        "You exceeded your maximum attempts. Please try after some time."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        member = Member.objects.get(user__username=username)

        if member.email_verified is False:
            verify_member_email(member, True)
        return Response([], status.HTTP_200_OK)


class MatchPredictionFieldStats(APIView):
    allowed_methods = ("GET",)
    serializer_class = PredictionStatSerializer

    def get(self, request):

        submission_field_id, submission_field_value, match_id = map(
            int,
            extract_from_request(
                request, "submission_field", "submission_field_value", "match"
            ),
        )

        # get member details
        member, memberships = member_memberships(self.request.user)
        member_group_ids = [m.member_group_id for m in memberships]

        # get match details
        match = Match.objects.get(id=match_id)
        match_type = match.match_type
        tournament_id = match.tournament_id

        submission_fields = SubmissionFieldConfig.objects.filter(
            field=submission_field_id,
            group_submissions_config__tournament=tournament_id,
            group_submissions_config__tournament_format=match_type,
            group_submissions_config__member_group__in=member_group_ids,
            group_submissions_config__submission_type=GroupSubmissionsConfig.MATCH_DATA_SUBMISSION,
        )

        if submission_fields.count() == 0:
            return {}

        submission_field = submission_fields[0]

        submission_field_name = SubmissionFieldConfig.FIELDS[submission_field_id]
        stat = None
        if (
            submission_field.field_model is SubmissionFieldConfig.FIELD_MODEL_PLAYER
            or submission_field.field_model
            is SubmissionFieldConfig.FIELD_MODEL_PLAYER_DEPENDANT_FIELD
        ):
            sn = stats.MODEL_STAT_NAMES[submission_field_name]
            stat = PlayerStat.objects.filter(
                player_id=submission_field_value, stat_name=sn
            )

        elif submission_field.field_model is SubmissionFieldConfig.FIELD_MODEL_TEAM:
            sn = stats.MODEL_STAT_NAMES[submission_field_name]
            stat = TeamStat.objects.filter(team_id=submission_field_value, stat_name=sn)

        else:
            stat = PredictionFieldStat.objects.filter(
                stat_name__in=stats.stat_names(submission_field_name, match_type)
            )

        stat = (
            stat.filter(match=match_id)
            .filter(is_latest=True)
            .filter(Q(member_group__in=member_group_ids) | Q(member_group__isnull=True))
            .filter(match_or_tournament_format=match_type)
        )

        d = stats.stat_names_and_ranges(submission_field_name, match_type)
        ranges = []
        for i in d:
            try:
                ranges.append({"stat_name": i[0], "range": i[1], "range_name": i[2]})
            except:
                pass

        return Response(
            {"data": PredictionStatSerializer(stat, many=True).data, "ranges": ranges}
        )


class TournamentPredictionFieldStats(APIView):
    allowed_methods = ("GET",)
    serializer_class = PredictionStatSerializer

    def get(self, request):
        (
            submission_field_id,
            submission_field_value,
            tournament_id,
            tournament_format,
        ) = map(
            int,
            extract_from_request(
                request,
                "submission_field",
                "submission_field_value",
                "tournament",
                "tournament_format",
            ),
        )

        member, memberships = member_memberships(self.request.user)
        member_group_ids = [m.member_group_id for m in memberships]

        submission_fields = SubmissionFieldConfig.objects.filter(
            field=submission_field_id,
            group_submissions_config__tournament=tournament_id,
            group_submissions_config__tournament_format=tournament_format,
            group_submissions_config__member_group__in=member_group_ids,
            group_submissions_config__submission_type=GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION,
        )

        if submission_fields.count() == 0:
            return {}

        submission_field = submission_fields[0]

        submission_field_name = SubmissionFieldConfig.FIELDS[submission_field_id]
        stat = None

        if submission_field.field_model is SubmissionFieldConfig.FIELD_MODEL_PLAYER:
            sn = stats.MODEL_STAT_NAMES[submission_field_name]
            stat = PlayerStat.objects.filter(
                player_id=submission_field_value, stat_name=sn
            )

        elif submission_field.field_model is SubmissionFieldConfig.FIELD_MODEL_TEAM:
            sn = stats.MODEL_STAT_NAMES[submission_field_name]
            stat = TeamStat.objects.filter(team_id=submission_field_value, stat_name=sn)

        else:
            stat = PredictionFieldStat.objects.filter(
                stat_name__in=stats.stat_names(submission_field_name, tournament_format)
            )

        stat = (
            stat.filter(tournament=tournament_id)
            .filter(is_latest=True)
            .filter(Q(member_group__in=member_group_ids) | Q(member_group__isnull=True))
            .filter(match_or_tournament_format=tournament_format)
        )

        ranges = []
        if submission_field_name in stats.RAW_NUMERIC_STATS:
            # update raw input value to stat_name so app side they can compare and
            # show stats by comparing range and stat
            for s in stat:
                s.stat_name = s.raw_input_value

            # get the range data from fields
            # generating it in a way so app don't need to handle this separately
            rs = submission_fields[0].build_range_data(match=None)
            ranges.append({"stat_name": str(0), "range": [0, 0], "range_name": str(0)})
            for r in rs:
                ranges.append(
                    {"stat_name": str(r), "range": [r, r], "range_name": str(r)}
                )
        else:
            d = stats.stat_names_and_ranges(submission_field_name, tournament_format)
            for i in d:
                try:
                    ranges.append(
                        {"stat_name": i[0], "range": i[1], "range_name": i[2]}
                    )
                except:
                    pass

        return Response(
            {"data": PredictionStatSerializer(stat, many=True).data, "ranges": ranges}
        )


class MatchPredictionFieldStatsDetails(ListAPIView):
    serializer_class = MemberSerializer

    def get_queryset(self):
        stat_name = extract_from_request(self.request, "stat_name")

        (submission_field_id, submission_field_value, member_group_id, match_id,) = map(
            int,
            extract_from_request(
                self.request,
                "submission_field",
                "submission_field_value",
                "member_group",
                "match",
            ),
        )

        # check if user is part of group
        member, memberships = member_memberships(self.request.user)
        member_group = MemberGroup.objects.get(id=member_group_id)
        if not has_membership(memberships, member_group_id):
            return []

        field_name = SubmissionFieldConfig.FIELDS[submission_field_id]

        match = Match.objects.get(id=match_id)
        match_type = match.match_type
        tournament_id = match.tournament_id

        submission_fields = SubmissionFieldConfig.objects.filter(
            field=submission_field_id,
            group_submissions_config__tournament=tournament_id,
            group_submissions_config__tournament_format=match_type,
            group_submissions_config__member_group=member_group_id,
            group_submissions_config__submission_type=GroupSubmissionsConfig.MATCH_DATA_SUBMISSION,
        )
        if submission_fields.count() == 0:
            return []

        submission_field = submission_fields[0]

        # checking first in membersubmission now to get id of latest selections of member
        filter_by = {
            "tournament": tournament_id,
            "match": match_id,
            "member_group": member_group_id,
            "is_valid": True,
            "member": member,
            "submission_format": match_type,
            "submission_type": GroupSubmissionsConfig.MATCH_DATA_SUBMISSION,
        }
        member_submissions = []
        for m in member_group.members.all():
            filter_by["member"] = m
            try:
                member_submissions.append(
                    MemberSubmission.objects.filter(**filter_by).latest("id")
                )
            except MemberSubmission.DoesNotExist:
                continue

        if len(member_submissions) == 0:
            return []

        ms = []
        ms = MemberSubmissionData.objects.filter(
            member_submission__in=member_submissions
            # field_name=field_name,
            # member_submission__is_valid= True,
            # member_submission__member_group=member_group_id,
            # member_submission__tournament=tournament_id,
            # member_submission__submission_type=GroupSubmissionsConfig.MATCH_DATA_SUBMISSION,
            # member_submission__submission_format=match_type,
        )

        if submission_field.field_model is SubmissionFieldConfig.FIELD_MODEL_PLAYER:
            ms = ms.filter(player=submission_field_value)

        elif (
            submission_field.field_model
            is SubmissionFieldConfig.FIELD_MODEL_PLAYER_DEPENDANT_FIELD
        ):
            ms = ms.filter(player=submission_field_value, field_name=field_name)

        elif submission_field.field_model is SubmissionFieldConfig.FIELD_MODEL_TEAM:
            ms = ms.filter(team=submission_field_value, field_name=field_name)

        else:
            # it will have data like 200-400, basis on range members will return
            data = stats.stat_names_and_ranges(field_name, match_type)
            ranges = {}
            for i in data:
                ranges[i[0]] = i[1]

            if not (stat_name in ranges.keys()):
                return []

            arr = []
            for m in ms:
                if m.value is not None:
                    if (int(m.value) >= ranges[stat_name][0]) and (
                        int(m.value) <= ranges[stat_name][1]
                    ):
                        arr.append(m.id)

            ms = ms.filter(field_name=field_name, id__in=arr)
        ms = ms.distinct("member_submission__member")
        members = [m.member_submission.member for m in ms]

        # sending unique record
        return members


class TournamentPredictionFieldStatsDetails(ListAPIView):
    serializer_class = MemberSerializer

    def get_queryset(self):
        stat_name = extract_from_request(self.request, "stat_name")
        (
            submission_field_id,
            member_group_id,
            tournament_id,
            tournament_format,
            submission_field_value,
        ) = map(
            int,
            extract_from_request(
                self.request,
                "submission_field",
                "member_group",
                "tournament",
                "tournament_format",
                "submission_field_value",
            ),
        )

        # check if user is part of group
        member, memberships = member_memberships(self.request.user)
        member_group = MemberGroup.objects.get(id=member_group_id)
        if not has_membership(memberships, member_group_id):
            return []

        field_name = SubmissionFieldConfig.FIELDS[submission_field_id]

        submission_fields = SubmissionFieldConfig.objects.filter(
            field=submission_field_id,
            group_submissions_config__tournament=tournament_id,
            group_submissions_config__tournament_format=tournament_format,
            group_submissions_config__member_group=member_group_id,
            group_submissions_config__submission_type=GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION,
        )
        if submission_fields.count() == 0:
            return []

        submission_field = submission_fields[0]

        # checking first in membersubmission now to get id of latest selections of member
        filter_by = {
            "tournament": tournament_id,
            "member_group": member_group_id,
            "is_valid": True,
            "member": member,
            "submission_format": tournament_format,
            "submission_type": GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION,
        }
        member_submissions = []
        for m in member_group.members.all():
            filter_by["member"] = m
            try:
                member_submissions.append(
                    MemberSubmission.objects.filter(**filter_by).latest("id")
                )
            except MemberSubmission.DoesNotExist:
                continue

        if len(member_submissions) == 0:
            return []

        ms = []
        ms = MemberSubmissionData.objects.filter(
            field_name=field_name,
            member_submission__in=member_submissions
            # member_submission__is_valid= True,
            # member_submission__member_group=member_group_id,
            # member_submission__tournament=tournament_id,
            # member_submission__submission_type=GroupSubmissionsConfig.TOURNAMENT_DATA_SUBMISSION,
            # member_submission__submission_format=tournament_format,
        )

        if submission_field.field_model is SubmissionFieldConfig.FIELD_MODEL_PLAYER:
            ms = ms.filter(player=submission_field_value)

        elif submission_field.field_model is SubmissionFieldConfig.FIELD_MODEL_TEAM:
            ms = ms.filter(team=submission_field_value)

        else:
            ranges = {}
            if field_name in stats.RAW_NUMERIC_STATS:
                rs = submission_fields[0].build_range_data(match=None)
                ranges[str(0)] = [0, 0]
                for r in rs:
                    ranges[str(r)] = [r, r]
            else:
                # it will have data like 200-400, basis on range members will return
                data = stats.stat_names_and_ranges(field_name, tournament_format)
                for i in data:
                    ranges[i[0]] = i[1]

            if not (stat_name in ranges.keys()):
                return []

            ms = ms.filter(
                field_name=field_name,
                value__gte=ranges[stat_name][0],
                value__lte=ranges[stat_name][1],
            )
        ms = ms.distinct("member_submission__member")
        members = [m.member_submission.member for m in ms]

        # sending unique record
        return members


class MemberProfile(APIView):
    def get(self, request):
        member = Member.objects.get(user=request.user)
        return Response(MemberProfileSerializer(member).data)

    def post(self, request, format=None):
        serializer = MemberProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        member, _ = member_memberships(request.user)
        data = serializer.data

        # updating profile details
        member.nick_name = data["nick_name"]
        member.country_id = data["country"]
        member.date_of_birth = data["date_of_birth"]
        member.gender = data["gender"]

        member.user.first_name = data["user"]["first_name"]
        member.user.last_name = data["user"]["last_name"]

        member.user.save()
        member.save()

        return Response(MemberProfileSerializer(member).data, status.HTTP_200_OK)


class MemberAvatar(APIView):
    def post(self, request):
        member, _ = member_memberships(request.user)

        # update profile image
        if request.FILES["avatar"]:
            avatar = request.FILES["avatar"]
            ms = AppMedia.objects.filter(member=member.id)

            if ms.count() == 0:
                m = AppMedia()
                m.member = member
                m.media_size = AppMedia.MEDIUM
                m.media_type = AppMedia.IMAGE
                m.media_file = avatar
                ms = [m]
            else:
                ms[0].media_file.save(avatar.name, avatar)
            ms[0].save()
            return Response(MemberProfileSerializer(member).data, status.HTTP_200_OK)

        return Response(
            {"non_field_errors": ["Send image to replace"]},
            status=status.HTTP_400_BAD_REQUEST,
        )


class MatchStatusView(APIView):
    allowed_methods = ("GET",)

    def get(self, request):
        data = []

        try:
            mids_str = [
                i.strip()
                for i in extract_from_request(request, "matches").strip().split(",")
            ]
            for mid in mids_str:
                try:
                    m = int(mid)
                    match = Match.objects.get(id=m)
                    data.append(match.submission_status())
                except Match.DoesNotExist:
                    logger.warn(f"Match Status called for unknown Match ID={m}")
                    continue
        except Exception as ex:
            logger.exception("Error in Match Status API call.")
            logger.exception(f"Request string: {mids_str}")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status.HTTP_200_OK)


# TODO test API calls with no backing data
# TODO test API calls with invald data
# TODO Refactor things where only difference is submission_type
# TODO Test with blank user
# TODO split out member_memberships, use as appropriate
