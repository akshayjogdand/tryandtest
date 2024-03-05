from collections import deque, OrderedDict

from django.db import models

from reversion import revisions as reversion

from python_field.python_field import PythonCodeField

from members.models import Member, MemberGroup

from fixtures.models import Match, Player, Team, Tournament, PlayerTournamentHistory

from stats.models import PlayerScores, BattingPerformance

from stats.utils import get_player_performance

from rules.models import (
    GroupPredictionSubmissionValidationResult,
    GroupPredictionScoringResult,
    GroupPostMatchPredictionScoringMethodResult,
    GroupLeaderBoardScoringMethodResult,
)

from sportappsite.constants import (
    TournamentFormats,
    draw_team,
    tie_team,
    tournament_tie_team,
    TournamentFormatToPTHAttrMapping,
    MatchTypes,
)

from app_media.utils import get_media


class MemberTournamentPrediction(models.Model):
    member = models.ForeignKey(Member, related_name="+", on_delete=models.PROTECT)
    member_group = models.ForeignKey(
        MemberGroup, related_name="+", on_delete=models.PROTECT
    )
    tournament = models.ForeignKey(
        Tournament, related_name="+", on_delete=models.PROTECT
    )
    prediction_format = models.IntegerField(
        null=False,
        blank=False,
        choices=TournamentFormats.type_choices(),
        default=TournamentFormats.T_TWENTY,
    )

    tournament_winning_team = models.ForeignKey(
        Team, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    runner_up = models.ForeignKey(
        Team, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    top_team_one = models.ForeignKey(
        Team, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    top_team_two = models.ForeignKey(
        Team, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    top_team_three = models.ForeignKey(
        Team, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    top_team_four = models.ForeignKey(
        Team, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    last_team = models.ForeignKey(
        Team, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    top_batsman_one = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    top_batsman_two = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    top_batsman_three = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    top_bowler_one = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    top_bowler_two = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    top_bowler_three = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    most_valuable_player_one = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    most_valuable_player_two = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    most_valuable_player_three = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    win_series_margin = models.IntegerField(null=True, blank=True)

    player_of_the_tournament_one = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    player_of_the_tournament_two = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    player_of_the_tournament_three = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    total_prediction_score = models.IntegerField(default=0, null=False, blank=False)

    grand_score = models.IntegerField(default=0, null=False, blank=False)

    def team_vars(self):
        od = OrderedDict()
        od["tournament_winning_team"] = self.tournament_winning_team
        od["runner_up"] = self.runner_up
        od["top_team_one"] = self.top_team_one
        od["top_team_two"] = self.top_team_two
        od["top_team_three"] = self.top_team_three
        od["top_team_four"] = self.top_team_four

        return od

    def top_team_vars(self):
        od = OrderedDict()
        od["top_team_one"] = self.top_team_one
        od["top_team_two"] = self.top_team_two
        od["top_team_three"] = self.top_team_three
        od["top_team_four"] = self.top_team_four

        return od

    def bowler_vars(self):
        od = OrderedDict()
        od["top_bowler_one"] = self.top_bowler_one
        od["top_bowler_two"] = self.top_bowler_two
        od["top_bowler_three"] = self.top_bowler_three

        return od

    def batsman_vars(self):
        od = OrderedDict()
        od["top_batsman_one"] = self.top_batsman_one
        od["top_batsman_two"] = self.top_batsman_two
        od["top_batsman_three"] = self.top_batsman_three

        return od

    def mvp_vars(self):
        od = OrderedDict()
        od["most_valuable_player_one"] = self.most_valuable_player_one
        od["most_valuable_player_two"] = self.most_valuable_player_two
        od["most_valuable_player_three"] = self.most_valuable_player_three
        return od

    def pot_vars(self):
        od = OrderedDict()
        od["player_of_the_tournament_one"] = self.player_of_the_tournament_one
        od["player_of_the_tournament_two"] = self.player_of_the_tournament_two
        od["player_of_the_tournament_three"] = self.player_of_the_tournament_three
        return od

    def table_column_ordering(self):
        config = GroupSubmissionsConfig.objects.get(
            member_group=self.member_group,
            tournament=self.tournament,
            tournament_format=self.prediction_format,
            submission_type=MemberSubmission.TOURNAMENT_DATA_SUBMISSION,
        )
        return map(lambda s: s.strip(), config.display_table_ordering.split(","))

    class Meta:
        unique_together = ("member", "tournament", "member_group", "prediction_format")

    def __str__(self):
        return "{} (group=[{}] tournament=[{}])".format(
            self.member.user.get_full_name(),
            self.member_group.group.name,
            self.tournament,
        )


class MemberPrediction(models.Model):
    member = models.ForeignKey(Member, related_name="+", on_delete=models.PROTECT)
    member_group = models.ForeignKey(
        MemberGroup, related_name="+", on_delete=models.PROTECT
    )
    match = models.ForeignKey(Match, related_name="+", on_delete=models.PROTECT)

    # Member submissions
    predicted_winning_team = models.ForeignKey(
        Team, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    predicted_winning_team_score = models.IntegerField(blank=True, null=True)

    predicted_first_wicket_gone_in_over = models.IntegerField(blank=True, null=True)

    predicted_win_margin_range = models.CharField(max_length=7, blank=True, null=True)

    super_player = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )
    player_one = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )
    player_two = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )
    player_three = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )
    player_four = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )
    player_five = models.ForeignKey(
        Player, related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )

    toss_winner = models.ForeignKey(
        Team, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )

    toss_outcome = models.IntegerField(
        blank=True, null=True, choices=Match.toss_outcomes, default=Match.UNKNOWN
    )

    toss_decision = models.IntegerField(
        blank=True, null=True, choices=Match.toss_decisions
    )

    player_with_most_sixes = models.ForeignKey(
        Player, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    player_with_most_fours = models.ForeignKey(
        Player, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    player_with_most_runs = models.ForeignKey(
        Player, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )
    player_with_most_wickets = models.ForeignKey(
        Player, related_name="+", null=True, blank=True, on_delete=models.PROTECT
    )

    total_extras = models.IntegerField(blank=True, null=True)
    total_free_hits = models.IntegerField(blank=True, null=True)
    total_run_outs = models.IntegerField(blank=True, null=True)
    total_catches = models.IntegerField(blank=True, null=True)
    total_wickets = models.IntegerField(blank=True, null=True)
    total_wides = models.IntegerField(blank=True, null=True)
    total_noballs = models.IntegerField(blank=True, null=True)
    total_byes = models.IntegerField(blank=True, null=True)
    total_legbyes = models.IntegerField(blank=True, null=True)
    total_bowled = models.IntegerField(blank=True, null=True)
    total_stumpings = models.IntegerField(blank=True, null=True)
    total_lbws = models.IntegerField(blank=True, null=True)
    total_sixes = models.IntegerField(blank=True, null=True)
    total_fours = models.IntegerField(blank=True, null=True)
    first_innings_run_lead = models.IntegerField(blank=True, null=True)

    game_bonus = models.IntegerField(blank=True, null=True, default=0)

    prediction_has_been_scored = models.BooleanField(default=False)
    prediction_submissions_locked = models.BooleanField(default=False)
    total_prediction_score = models.IntegerField(blank=False, null=False, default=0)

    player_one_score = models.ForeignKey(
        PlayerScores, null=True, blank=True, related_name="+", on_delete=models.PROTECT
    )
    player_two_score = models.ForeignKey(
        PlayerScores, null=True, blank=True, related_name="+", on_delete=models.PROTECT
    )
    player_three_score = models.ForeignKey(
        PlayerScores, null=True, blank=True, related_name="+", on_delete=models.PROTECT
    )
    player_four_score = models.ForeignKey(
        PlayerScores, null=True, blank=True, related_name="+", on_delete=models.PROTECT
    )
    player_five_score = models.ForeignKey(
        PlayerScores, null=True, blank=True, related_name="+", on_delete=models.PROTECT
    )

    super_player_score = models.FloatField(null=True, blank=True)

    winning_team = models.ForeignKey(
        Team, null=True, blank=True, related_name="+", on_delete=models.PROTECT
    )
    winning_team_score = models.IntegerField(null=True, blank=True)
    winning_team_calculated_winning_score = models.IntegerField(null=True, blank=True)
    winning_team_final_winning_score = models.IntegerField(null=True, blank=True)

    prediction_scores = models.ForeignKey(
        "PredictionScores",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.PROTECT,
    )

    post_prediction_scores = models.ForeignKey(
        "PostPredictionScores",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.PROTECT,
    )

    leaderboard_scores = models.ForeignKey(
        "LeaderBoardScores",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return "{} (group=[{}] match=[{}])".format(
            self.member.user.get_full_name(), self.member_group.group.name, self.match
        )

    def player_vars_to_player_scores_vars(self):
        return {
            "player_one": "player_one_score",
            "player_two": "player_two_score",
            "player_three": "player_three_score",
        }

    def player_set_vars(self):
        od = OrderedDict()

        od["player_one"] = self.player_one
        od["player_two"] = self.player_two
        od["player_three"] = self.player_three

        return od

    def batting_performances(self):
        perfs = deque()

        for player in self.player_set_vars().values():
            performance = get_player_performance(player, self.match, BattingPerformance)
            perfs.append(performance)

        return perfs

    def batting_performance(self, player):
        for p in self.player_set_vars().values():
            if p == player:
                return get_player_performance(player, self.match, BattingPerformance)

    def was_all_out(self, team):
        count = 0
        for bp in BattingPerformance.objects.filter(match=self.match, team=team):

            if bp.was_out == BattingPerformance.WO_OUT:
                count = count + 1

            if (bp.was_out == BattingPerformance.WO_NOT_OUT) and (
                bp.dismissal == BattingPerformance.RETIRED_HURT
            ):
                count = count + 1

        return count == 10

    # TODO -- staticmethod
    def get_prediction_for_match(self, match, member, group):
        try:
            return MemberPrediction.objects.get(
                match=match, member=member, member_group=group
            )
        except MemberPrediction.DoesNotExist:
            return None

    def was_submitted(self):
        return any(
            (
                self.player_one,
                self.player_two,
                self.player_three,
                self.predicted_winning_team,
            )
        )

    def no_pre_toss_submission(self):
        return (
            MemberSubmission.objects.filter(
                member=self.member,
                member_group=self.member_group,
                match=self.match,
                is_post_toss=False,
            ).count()
            == 0
        )

    def player_scores(self):
        return [
            s
            for s in [
                self.player_one_score,
                self.player_two_score,
                self.player_three_score,
                self.player_four_score,
                self.player_five_score,
            ]
            if s
        ]

    def table_column_ordering(self):
        config = GroupSubmissionsConfig.objects.get(
            member_group=self.member_group,
            tournament=self.match.tournament,
            tournament_format=self.match.match_type,
            submission_type=MemberSubmission.MATCH_DATA_SUBMISSION,
        )
        return map(lambda s: s.strip(), config.display_table_ordering.split(","))

    class Meta:
        unique_together = ("member", "match", "member_group")


class MemberSubmission(models.Model):
    MATCH_DATA_SUBMISSION = 1
    TOURNAMENT_DATA_SUBMISSION = 2

    type_choices = (
        (MATCH_DATA_SUBMISSION, "Match"),
        (TOURNAMENT_DATA_SUBMISSION, "Tournament"),
    )

    member = models.ForeignKey(
        Member, blank=False, null=False, on_delete=models.PROTECT
    )
    member_group = models.ForeignKey(
        MemberGroup, blank=False, null=False, on_delete=models.PROTECT
    )
    match = models.ForeignKey(Match, blank=True, null=True, on_delete=models.PROTECT)
    tournament = models.ForeignKey(
        Tournament, blank=False, null=False, on_delete=models.PROTECT
    )
    submission_time = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    request_time = models.DateTimeField(blank=False, null=False)
    submission_type = models.IntegerField(blank=False, null=False, choices=type_choices)
    submission_format = models.IntegerField(
        null=False,
        blank=False,
        choices=MatchTypes.type_choices(),
        default=MatchTypes.T_TWENTY.value,
    )

    is_valid = models.BooleanField(blank=False, null=False, default=False)
    converted_to_prediction = models.BooleanField(
        blank=False, null=False, default=False, editable=False
    )
    validation_errors = models.TextField(null=True, blank=True)
    is_post_toss = models.BooleanField(null=False, default=False)

    is_post_toss = models.BooleanField(null=False, default=False)

    crossposted = models.BooleanField(null=False, default=False)
    crossposted_from = models.IntegerField(null=True, blank=True)

    p_a_computed = models.BooleanField(null=False, default=False)

    def __str__(self):
        x = self.match if self.match else self.tournament
        return "{}, in {} for: {}".format(self.member, self.member_group, x)

    def all_submitted_fields_and_values(self):
        return {
            submitted_field.field_name: submitted_field.field_value()
            for submitted_field in self.submission_data.all()
        }

    def players(self):
        return {
            submitted_field.field_name: submitted_field.player
            for submitted_field in self.submission_data.all()
            if submitted_field.player is not None
        }

    def player_set(self):
        return set(self.players().values())

    def teams(self):
        return {
            submitted_field.field_name: submitted_field.team
            for submitted_field in self.submission_data.all()
            if submitted_field.team is not None
        }

    def not_teams_or_players(self):
        return self.values()

    def are_teams_different(self, other_submission):
        my_teams = set(self.teams().values())
        other_teams = set(other_submission.teams().values())

        if len(my_teams) == len(other_teams):
            return len(my_teams.difference(other_teams)) != 0
        else:
            return False

    def are_non_team_non_player_values_different(self, other_submission):
        mine = self.not_teams_or_players()
        others = other_submission.not_teams_or_players()

        if len(mine) != len(others):
            return False

        for k, v in mine.items():
            if k not in others:
                return True

            if v != others[k]:
                return True

        return False

    def value_changes(self, other_submission):
        mine = self.not_teams_or_players()
        others = other_submission.not_teams_or_players()
        new_values = {}
        old_values = {}

        if mine == others:
            return new_values, old_values

        for k, v in mine.items():
            # New field, so it is a change
            if k not in others:
                new_values[k] = v

            # Same field value but value changed
            elif v != others[k]:
                new_values[k] = v
                old_values[k] = others[k]

        # Now check the other way
        for k, v in others.items():
            # New field, so it is a change
            if k not in mine:
                old_values[k] = v

        return new_values, old_values

    def has_only_teams_or_players(self):
        return len(self.values()) == 0

    def values(self):
        return {
            submitted_field.field_name: submitted_field.value
            for submitted_field in self.submission_data.all()
            if submitted_field.value is not None
        }

    def field(self, field_name):
        for d in self.submission_data.all():
            if d.field_name == field_name:
                return d

    def field_value(self, field_name):
        field = self.field(field_name)

        if field:
            if field.value:
                return field.value
            elif field.player:
                return field.player
            elif field.team:
                return field.team

    def table_column_ordering(self):
        config = GroupSubmissionsConfig.objects.get(
            member_group=self.member_group,
            tournament=self.tournament,
            submission_type=self.submission_type,
            tournament_format=self.submission_format,
        )
        return map(lambda s: s.strip(), config.display_table_ordering.split(","))


class MemberSubmissionData(models.Model):

    TYPE_TO_ATTR_NAME_MAP = {Player: "player", Team: "team", int: "value", str: "value"}

    member_submission = models.ForeignKey(
        MemberSubmission,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="submission_data",
    )
    field_name = models.CharField(max_length=100, null=False)
    value = models.CharField(max_length=100, null=True, blank=True)
    player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return "{}, {}".format(self.id, self.member_submission)

    def set_value(self, attr_type, value):
        setattr(self, self.TYPE_TO_ATTR_NAME_MAP[attr_type], value)

    def field(self):
        return SubmissionFieldConfig.FIELD_NAME_TO_ID_MAP[self.field_name]

    def field_value(self):
        if self.value:
            return self.value
        if self.player:
            return self.player
        if self.team:
            return self.team

    def field_type(self):
        if self.value:
            return int
        if self.player:
            return Player
        if self.team:
            return Team


class GroupSubmissionsConfig(models.Model):

    MATCH_DATA_SUBMISSION = 1
    TOURNAMENT_DATA_SUBMISSION = 2

    type_choices = (
        (MATCH_DATA_SUBMISSION, "Match"),
        (TOURNAMENT_DATA_SUBMISSION, "Tournament"),
    )

    member_group = models.ForeignKey(
        MemberGroup, blank=False, null=False, on_delete=models.CASCADE
    )
    tournament = models.ForeignKey(
        Tournament, blank=False, null=False, on_delete=models.PROTECT
    )
    tournament_format = models.IntegerField(
        null=False,
        blank=False,
        choices=TournamentFormats.type_choices(),
        default=TournamentFormats.T_TWENTY.value,
    )
    submission_notes = models.TextField(max_length=2000, null=True, blank=True)
    submission_type = models.IntegerField(
        null=False, blank=False, choices=type_choices, default=MATCH_DATA_SUBMISSION
    )
    display_table_ordering = models.TextField(
        max_length=500, null=False, blank=False, default=""
    )
    active_from = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date-Time from which this set of fields is allowed.",
    )
    active_to = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date-Time to which this set of fields is allowed.",
    )

    class Meta:
        unique_together = (
            "tournament",
            "submission_type",
            "member_group",
            "tournament_format",
        )

    def __str__(self):
        if self.submission_type == self.MATCH_DATA_SUBMISSION:
            t = "Match"
        else:
            t = "Tournament"

        return "{} Submission Fields for: {} in {}".format(
            t, self.member_group.group.name, self.tournament.name
        )

    def submission_fields_config_as_json(self, match, lock_all=False):
        field_properties = (
            "form_order",
            "description",
            "field_model",
            "field",
            "is_compulsory",
            "form_category",
            "is_enabled",
            "range_data",
            "is_reactive",
            "reactions",
        )
        config = []

        for field in self.submission_fields.all():
            field_match_tester = eval(field.enable_for_matches, {})

            if field_match_tester(match):
                field_json = {}
                for prop in field_properties:
                    field_json[prop] = getattr(field, prop)

                field_json["range_data"] = field.build_range_data(match)

                if field.is_reactive:
                    field_json["reactions"] = field.build_reactions(match)

                config.append(field_json)

        if lock_all:
            for field in config:
                if field["field"] != SubmissionFieldConfig.SUPER_PLAYER_FIELD_ID:
                    field["is_enabled"] = False

        return config

    def adjust_tournament_team_names(self):
        teams = list(
            set(
                [
                    ph.team
                    for ph in PlayerTournamentHistory.objects.filter(
                        tournament=self.tournament
                    ).order_by("team__name")
                ]
            )
        )

        if self.tournament.bi_lateral is True:
            teams.append(tournament_tie_team())

        return teams

    def adjust_team_names(self, match):
        teams = match.teams()
        match_teams = list()

        if match.match_type == Match.TEST:
            for t in teams:
                match_teams.append(
                    {
                        "team_id": t.id,
                        "team_name": "Win: {}".format(t.name),
                        "abbreviation": "Win: {}".format(t.abbreviation),
                        "media": get_media({"team": t}),
                    }
                )

            match_teams.extend(
                (
                    {
                        "team_id": draw_team().id,
                        "team_name": draw_team().name,
                        "abbreviation": draw_team().abbreviation,
                        "media": get_media({"team": draw_team()}),
                    },
                    {
                        "team_id": tie_team().id,
                        "team_name": tie_team().name,
                        "abbreviation": tie_team().abbreviation,
                        "media": get_media({"team": tie_team()}),
                    },
                )
            )

        else:
            for team in teams:
                match_teams.append(
                    {
                        "team_id": team.id,
                        "team_name": team.name,
                        "abbreviation": team.abbreviation,
                        "media": get_media({"team": team}),
                    }
                )

        return match_teams

    def open_match_data(self, match):
        match_data = {}
        match_data["id"] = match.id
        match_data["match_name"] = match.name
        match_data["short_display_name"] = match.short_display_name
        match_data["players"] = list()
        match_data["submission_fields"] = self.submission_fields_config_as_json(match)

        players = match.tournament_players()

        for player in players:
            match_data["players"].append(
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "player_hand": Player.hands[player.player_hand],
                    "skill": player.skill(),
                    "media": get_media({"player": player}),
                }
            )

        match_data["teams"] = self.adjust_team_names(match)

        return match_data

    def post_toss_without_previous_submission_fields(self, match):
        config = self.submission_fields_config_as_json(match, lock_all=True)
        for field in config:
            if field["field"] == SubmissionFieldConfig.PLAYER_ONE_FIELD:
                field["is_enabled"] = True
                field["is_compulsory"] = True
            else:
                field["is_enabled"] = False
                field["is_compulsory"] = False

        return config

    def unlock_post_toss_fields(self, match, member, playing_eleven):
        # in post toss scenario, lock everything
        submission_fields = self.submission_fields_config_as_json(match, lock_all=True)

        pre_toss_submissions = MemberSubmission.objects.filter(
            match=match,
            member_group=self.member_group,
            member=member,
            is_post_toss=False,
            is_valid=True,
        ).order_by("-id")

        if pre_toss_submissions.exists():
            last_valid_pre_toss_submission = pre_toss_submissions.first()
        else:
            return self.post_toss_without_previous_submission_fields(match)

        # Special case, no Player in pre-toss Submission is P-XI.
        original_players = last_valid_pre_toss_submission.player_set()
        if len(original_players.intersection(set(playing_eleven))) == 0:
            return self.post_toss_without_previous_submission_fields(match)

        to_unlock = []
        sp_range_fields = []

        for submitted_data in last_valid_pre_toss_submission.submission_data.all():
            if submitted_data.field_type() == Player:
                selected_player = submitted_data.field_value()

                if selected_player not in playing_eleven:
                    to_unlock.append(submitted_data.field_name)

                # Changing Super Player post toss to Player in this field is allowed.
                else:
                    sp_range_fields.append(submitted_data.field_name)

        sp_range = f"lambda m,s: {sp_range_fields}"
        sfc = SubmissionFieldConfig(
            range_data=sp_range,
            field=SubmissionFieldConfig.SUPER_PLAYER_FIELD_ID,
            field_model=SubmissionFieldConfig.FIELD_MODEL_PLAYER_DEPENDANT_FIELD,
        )

        for field in submission_fields:
            field_name = SubmissionFieldConfig.FIELDS[field["field"]]
            if field_name in to_unlock:
                field["is_enabled"] = True
                field["is_compulsory"] = False
                field["field_model"] = SubmissionFieldConfig.FIELD_MODEL_PLAYER

            if field_name == "super_player":
                field["is_enabled"] = len(sp_range_fields) > 0
                field["is_compulsory"] = len(sp_range_fields) > 0
                field["range_data"] = sfc.build_range_data(match)
                field[
                    "field_model"
                ] = SubmissionFieldConfig.FIELD_MODEL_PLAYER_DEPENDANT_FIELD

        return submission_fields

    def post_toss_match_data(self, match, member):
        match_data = {}
        match_data["id"] = match.id
        match_data["match_name"] = match.name
        match_data["short_display_name"] = match.short_display_name
        match_data["teams"] = self.adjust_team_names(match)
        match_data["players"] = list()

        playing_eleven = match.squad_players()

        for player in playing_eleven:
            match_data["players"].append(
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "skill": player.skill(),
                    "media": get_media({"player": player}),
                }
            )

        submission_fields = self.unlock_post_toss_fields(match, member, playing_eleven)
        match_data["submission_fields"] = submission_fields

        return match_data

    def allowed_match_submission_data(self, match_id, member):
        match = Match.objects.get(id=match_id)
        if match.submissions_allowed:
            return self.open_match_data(match)
        elif match.post_toss_changes_allowed:
            return self.post_toss_match_data(match, member)

    def allowed_tournament_submission_data(self):
        allowed_data = {}
        allowed_data["players"] = []
        allowed_data["teams"] = []
        if not self.tournament.submissions_allowed:
            return {}

        player_format_attr = "{}".format(
            TournamentFormatToPTHAttrMapping.get(self.tournament_format)
        )

        pth_filters = {
            player_format_attr: True,
            "tournament": self.tournament,
        }
        players = (
            PlayerTournamentHistory.objects.filter(**pth_filters)
            .order_by("team", "player__name")
            .exclude(status=PlayerTournamentHistory.PLAYER_WITHDRAWN)
        )

        players_details = [ph.player for ph in players]

        teams = self.adjust_tournament_team_names()

        for player in players_details:
            allowed_data["players"].append(
                {
                    "player_id": player.id,
                    "player_name": player.name,
                    "player_hand": Player.hands[player.player_hand],
                    "skill": player.skill(),
                    "media": get_media({"player": player}),
                }
            )

        for team in teams:
            allowed_data["teams"].append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "team_abbreviation": team.abbreviation,
                    "media": get_media({"team": team}),
                }
            )

        return allowed_data

    def allowed_matches(self):
        return Match.objects.filter(
            tournament=self.tournament,
            submissions_allowed=True,
            post_toss_changes_allowed=False,
        ).order_by("match_number")

    def allowed_post_toss_changes_matches(self):
        return Match.objects.filter(
            tournament=self.tournament,
            submissions_allowed=False,
            post_toss_changes_allowed=True,
        ).order_by("match_number")


class ControlledGroupSubmissionsConfig(GroupSubmissionsConfig):
    def __str__(self):
        if self.submission_type == self.MATCH_DATA_SUBMISSION:
            t = "Match"
        else:
            t = "Tournament"

        return "{} Controlled Submission Fields for: {} in {}".format(
            t, self.member_group.group.name, self.tournament.name
        )


class SubmissionFieldConfig(models.Model):
    MATCH_NUMBER_CHECK_LAMBDA_STR = "lambda match: True"
    RANGE_DATA_LAMBDA_STR = "lambda match, submission_config: []"

    FIELD_MODEL_TEAM = 0
    FIELD_MODEL_PLAYER = 1
    FIELD_MODEL_STRING = 2
    FIELD_MODEL_NUMBER = 3
    FIELD_MODEL_FLOAT = 4
    FIELD_MODEL_NUMBER_RANGE = 5
    FIELD_MODEL_STRING_RANGE = 6
    FIELD_MODEL_REGEX = 7
    FIELD_MODEL_PLAYER_DEPENDANT_FIELD = 8
    FIELD_MODEL_TEAM_DEPENDANT_FIELD = 9

    FIELD_MODEL_TYPE_MAP = {
        FIELD_MODEL_TEAM: Team,
        FIELD_MODEL_PLAYER: Player,
        FIELD_MODEL_NUMBER: int,
        FIELD_MODEL_STRING: str,
        FIELD_MODEL_FLOAT: float,
        FIELD_MODEL_NUMBER_RANGE: int,
        FIELD_MODEL_STRING_RANGE: str,
        FIELD_MODEL_REGEX: str,
        FIELD_MODEL_PLAYER_DEPENDANT_FIELD: Player,
        FIELD_MODEL_TEAM_DEPENDANT_FIELD: Team,
    }

    SUPER_PLAYER_FIELD_ID = 5

    PLAYER_ONE_FIELD = 6

    # DO NOT change the numeric key in the structure below
    # unless you know what you are doing!
    FIELDS = {
        4: "predicted_winning_team",
        SUPER_PLAYER_FIELD_ID: "super_player",
        PLAYER_ONE_FIELD: "player_one",
        7: "player_two",
        8: "player_three",
        9: "player_four",
        10: "player_five",
        11: "toss_winner",
        12: "toss_outcome",
        13: "toss_decision",
        14: "player_with_most_sixes",
        15: "player_with_most_fours",
        16: "player_with_most_runs",
        17: "player_with_most_wickets",
        18: "total_extras",
        20: "total_run_outs",
        21: "total_catches",
        22: "total_wickets",
        23: "total_wides",
        24: "total_noballs",
        25: "total_byes",
        26: "total_legbyes",
        27: "total_bowled",
        28: "total_stumpings",
        29: "total_lbws",
        30: "total_sixes",
        31: "total_fours",
        32: "predicted_winning_team_score",
        33: "predicted_first_wicket_gone_in_over",
        34: "tournament_winning_team",
        36: "runner_up",
        37: "top_team_three",
        38: "top_team_four",
        39: "top_batsman_one",
        40: "top_batsman_two",
        41: "top_batsman_three",
        42: "top_bowler_one",
        43: "top_bowler_two",
        44: "top_bowler_three",
        45: "most_valuable_player_one",
        46: "most_valuable_player_two",
        47: "most_valuable_player_three",
        48: "last_team",
        49: "win_series_margin",
        50: "first_innings_run_lead",
        51: "general_field_one",
        52: "general_field_two",
        53: "general_field_three",
        54: "general_field_four",
        55: "general_field_five",
        60: "top_team_one",
        61: "top_team_two",
        62: "player_of_the_tournament_one",
        63: "player_of_the_tournament_two",
        64: "player_of_the_tournament_three",
    }

    FIELD_NAME_TO_ID_MAP = {v: k for k, v in FIELDS.items()}

    model_choices = (
        (FIELD_MODEL_TEAM, "Team"),
        (FIELD_MODEL_PLAYER, "Player"),
        (FIELD_MODEL_STRING, "String"),
        (FIELD_MODEL_NUMBER, "Number"),
        (FIELD_MODEL_FLOAT, "Float"),
        (FIELD_MODEL_NUMBER_RANGE, "Number Range"),
        (FIELD_MODEL_STRING_RANGE, "String Range"),
        (FIELD_MODEL_REGEX, "Regex"),
        (FIELD_MODEL_PLAYER_DEPENDANT_FIELD, "Player Dependant Field"),
        (FIELD_MODEL_TEAM_DEPENDANT_FIELD, "Team Dependant Field"),
    )

    fields_choices = [(k, v) for k, v in FIELDS.items()]

    group_submissions_config = models.ForeignKey(
        GroupSubmissionsConfig,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="submission_fields",
    )
    form_order = models.IntegerField(blank=False, null=False)
    field = models.IntegerField(blank=False, null=False, choices=fields_choices)
    description = models.CharField(max_length=100, blank=False, null=False)
    is_compulsory = models.BooleanField(default=False, null=False, blank=False)
    is_enabled = models.BooleanField(default=True, null=False, blank=True)
    is_reactive = models.BooleanField(default=False, null=False, blank=False)
    reactions = PythonCodeField(
        blank=True,
        null=True,
        max_length=500,
        help_text=(
            """[ { 'name': 'Disable on Tie', """,
            """    'match_regex': lambda match, field_config: '^xx$', """,
            """    'reaction_targets': lambda match, field_config: [...] """,
            """    'field_value': '0', """,
            """    'field_status: 'disabled' } ] """,
        ),
    )
    enable_for_matches = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        default=MATCH_NUMBER_CHECK_LAMBDA_STR,
        help_text="e.g. lambda match: match.match_number in [1,2,3]",
    )
    field_model = models.IntegerField(null=True, blank=True, choices=model_choices)
    form_category = models.CharField(blank=True, null=True, max_length=150)
    range_data = PythonCodeField(
        blank=True,
        null=True,
        max_length=150,
        help_text="lambda: match, field_instance: []",
    )

    def get_model_type(self):
        return self.FIELD_MODEL_TYPE_MAP.get(self.field_model)

    def __str__(self):
        return "Submission Field: {} for: {}".format(
            self.FIELDS.get(self.field), self.group_submissions_config
        )

    def build_range_data(self, match):
        range_data = []

        if self.field_model in (
            self.FIELD_MODEL_NUMBER_RANGE,
            self.FIELD_MODEL_STRING_RANGE,
            self.FIELD_MODEL_REGEX,
            self.FIELD_MODEL_PLAYER_DEPENDANT_FIELD,
            self.FIELD_MODEL_TEAM_DEPENDANT_FIELD,
        ):
            if self.range_data is not None:
                range_lambda = eval(self.range_data, {})
                range_data = range_lambda(match, self)

        if self.field_model in (
            self.FIELD_MODEL_TEAM_DEPENDANT_FIELD,
            self.FIELD_MODEL_PLAYER_DEPENDANT_FIELD,
        ):
            # Check if the data is a Submission Field
            rd_copy = range_data.copy()
            for f in rd_copy:
                if f in self.FIELD_NAME_TO_ID_MAP:
                    range_data.remove(f)
                    range_data.append(self.FIELD_NAME_TO_ID_MAP[f])

        return range_data

    def build_reaction_targets(self, match, reaction_targets_fn):
        if not self.is_reactive:
            return

        targets = reaction_targets_fn(match, self)
        # Expected to give a list []
        targets_copy = targets.copy()

        for f in targets:
            if f in self.FIELD_NAME_TO_ID_MAP:
                targets_copy.remove(f)
                targets_copy.append(self.FIELD_NAME_TO_ID_MAP[f])

        return targets_copy

    def build_reactions(self, match):
        if not self.is_reactive:
            return

        built_reactions = []
        reactions_fn = eval(self.reactions)
        reactions = reactions_fn(match, self)
        # Expected to give a list []

        for r in reactions:
            r_copy = r.copy()
            r_copy["match_regex"] = r["match_regex"](match, self)
            r_copy["reaction_targets"] = self.build_reaction_targets(
                match, r["reaction_targets"]
            )
            built_reactions.append(r_copy)

        return built_reactions


class TouramentPredictionScore(models.Model):
    prediction = models.ForeignKey(
        MemberTournamentPrediction,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="scores",
    )
    team_one = models.ForeignKey(
        Team, null=True, on_delete=models.PROTECT, blank=True, related_name="+"
    )
    team_two = models.ForeignKey(
        Team, null=True, on_delete=models.PROTECT, blank=True, related_name="+"
    )
    team_three = models.ForeignKey(
        Team, null=True, on_delete=models.PROTECT, blank=True, related_name="+"
    )
    team_four = models.ForeignKey(
        Team, null=True, on_delete=models.PROTECT, blank=True, related_name="+"
    )
    last_team = models.ForeignKey(
        Team, null=True, on_delete=models.PROTECT, blank=True, related_name="+"
    )
    player = models.ForeignKey(
        Player, null=True, on_delete=models.PROTECT, blank=True, related_name="+"
    )
    rule = models.CharField(max_length=300, blank=False, null=False)
    points = models.IntegerField(null=False, default=0)

    def __str__(self):
        return "TouramentPredictionScore for {}".format(self.prediction)


class PredictionScores(models.Model):
    scored_on = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    total_score = models.FloatField(null=False, blank=False, default=0.0)
    detailed_scoring = models.ManyToManyField(GroupPredictionScoringResult)

    class Meta:
        verbose_name_plural = "Prediction Scores"

    def __str__(self):
        return "Prediction Scores id={} [{}]".format(self.id, self.total_score)


class PostPredictionScores(models.Model):
    scored_on = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    total_score = models.FloatField(null=False, blank=False, default=0.0)
    detailed_scoring = models.ManyToManyField(
        GroupPostMatchPredictionScoringMethodResult
    )

    class Meta:
        verbose_name_plural = "Post Prediction scores"

    def __str__(self):
        return "Post Prediction Scores id={} [{}]".format(self.id, self.total_score)


class LeaderBoardScores(models.Model):
    scored_on = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    total_score = models.FloatField(null=False, blank=False, default=0.0)
    detailed_scoring = models.ManyToManyField(GroupLeaderBoardScoringMethodResult)

    class Meta:
        verbose_name_plural = "Leader Board scores"

    def __str__(self):
        return "Leader Board Scores id={} [{}]".format(self.id, self.total_score)


class PredictionSubmissionValidations(models.Model):
    scored_on = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    total_score = models.FloatField(null=False, blank=False, default=0)
    detailed_scoring = models.ManyToManyField(GroupPredictionSubmissionValidationResult)

    class Meta:
        verbose_name_plural = "Prediction Submission validations"


reversion.register(MemberPrediction)
reversion.register(PredictionScores)
reversion.register(PredictionSubmissionValidations)
