import arrow

from enum import IntEnum, unique

from django.db import models

from timezone_field.fields import TimeZoneField

from python_field.python_field import PythonCodeField

from python_field.utils import is_code_and_lambda

from reversion import revisions as reversion

from rules.models import (
    PlayerScoringMethod,
    PredictionScoringMethod,
    PredictionSubmissionValidationRule,
    PostMatchPredictionScoringMethod,
    LeaderBoardScoringMethod,
    TournamentScoringMethod,
)


class Club(models.Model):
    name = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return self.name


@unique
class TournamentFormats(IntEnum):
    ONE_DAY = 1
    T_TWENTY = 2
    TEST = 3

    @classmethod
    def type_choices(self):
        return (
            (self.ONE_DAY.value, "One Day"),
            (self.T_TWENTY.value, "T-20"),
            (self.TEST.value, "Test match"),
        )

    @classmethod
    def type_choices_str(self):
        l = []
        for v, s in self.type_choices():
            l.append("{}={}".format(s, v))

        return "\n".join(l)


class Tournament(models.Model):
    # Tournament Levels
    T_LEVEL_DOMESTIC = 0
    T_LEVEL_INTERNATIONAL = 1

    _LONG_NAME_LAMBDA = (
        "lambda match: '{}, {}: {} vs. {}'.format("
        "match.tournament.name, match.reference_name, "
        "match.team_one.team.name, match.team_two.team.name)"
    )

    _SHORT_NAME_LAMBDA = (
        "lambda match: '{}, {}: {} vs. {}'.format("
        "match.tournament.abbreviation, match.reference_name, "
        "match.team_one.team.abbreviation, match.team_two.team.abbreviation)"
    )

    tournament_levels = (
        (T_LEVEL_INTERNATIONAL, "International"),
        (T_LEVEL_DOMESTIC, "Domestic"),
    )

    tournament_level = models.IntegerField(
        null=False, blank=False, default=T_LEVEL_DOMESTIC, choices=tournament_levels
    )
    club = models.ForeignKey(Club, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=100, blank=False)
    abbreviation = models.CharField(max_length=30, blank=False, default="", null=False)
    start_date = models.DateTimeField("Start Date", blank=False, null=True)
    end_date = models.DateTimeField("End Date", blank=False, null=True)
    host_country = models.ForeignKey(
        "Country", null=True, blank=False, on_delete=models.PROTECT
    )
    team_one = models.ForeignKey(
        "Team",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="tournament_team_one",
    )
    team_two = models.ForeignKey(
        "Team",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="tournament_team_two",
    )
    bi_lateral = models.BooleanField(default=False, null=False)
    submissions_allowed = models.BooleanField(default=False, null=False)
    is_active = models.BooleanField(default=False, null=False)
    t20_series = models.BooleanField(default=False, null=False)
    odi_series = models.BooleanField(default=False, null=False)
    test_series = models.BooleanField(default=False, null=False)

    match_naming_strategy = PythonCodeField(
        default=_LONG_NAME_LAMBDA,
        blank=False,
        null=False,
        max_length=200,
        validators=(is_code_and_lambda,),
    )

    short_display_name_strategy = PythonCodeField(
        default=_SHORT_NAME_LAMBDA,
        blank=False,
        null=False,
        max_length=200,
        validators=(is_code_and_lambda,),
    )

    def __str__(self):
        return self.name

    def total_matches(self, match_type):
        return Match.objects.filter(tournament=self, match_type=match_type).count()

    def players(self):
        return set(
            [
                pth.player
                for pth in PlayerTournamentHistory.objects.filter(tournament=self)
            ]
        )

    def teams(self):
        return set(
            [
                pth.team
                for pth in PlayerTournamentHistory.objects.filter(tournament=self)
            ]
        )

    def series(self):
        t = []

        if self.t20_series:
            t.append(("t20_series", Match.T_TWENTY))

        if self.test_series:
            t.append(("test_series", Match.TEST))

        if self.odi_series:
            t.append(("odi_series", Match.ONE_DAY))

        return t

    def auto_discover_series(self):
        t = set()

        for m in Match.objects.filter(tournament=self):
            if m.match_type == Match.T_TWENTY:
                t.add(("t20_series", Match.T_TWENTY))

            if m.match_type == Match.TEST:
                t.add(("test_series", Match.TEST))

            if m.match_type == Match.ONE_DAY:
                t.add(("odi_series", Match.ONE_DAY))

        return t

    def submission_status(self):
        status_str = "Closed"

        if self.submissions_allowed:
            status_str = "Open"

        return {
            "id": self.id,
            "submission_status": status_str,
            "start_time_utc": self.start_date,
        }


class Timezone(models.Model):
    tz = TimeZoneField(null=False, blank=False)

    def __str__(self):
        return self.tz.zone


class Country(models.Model):
    name = models.CharField(max_length=100, blank=False)
    code = models.CharField(max_length=3, blank=True)

    # phone number code e.g.+91 for india
    calling_code = models.CharField(max_length=3, blank=True)
    timezones = models.ManyToManyField(Timezone)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "countries"


class City(models.Model):
    name = models.CharField(max_length=100, blank=False)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    timezone = models.ForeignKey(
        Timezone, null=True, on_delete=models.PROTECT, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "cities"


class Venue(models.Model):
    name = models.CharField(max_length=100, blank=False)
    city = models.ForeignKey(City, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "venues"


class Player(models.Model):
    ALLROUNDER = 0
    BATSMAN = 1
    BOWLER = 2
    KEEPER = 3
    LEFT_HAND = 4
    RIGHT_HAND = 5

    skill_choices = (
        (ALLROUNDER, "All-rounder"),
        (BATSMAN, "Batsman"),
        (BOWLER, "Bowler"),
        (KEEPER, "Wicket-keeper"),
    )

    hands_choices = ((LEFT_HAND, "Left Handed"), (RIGHT_HAND, "Right Handed"))

    hands = {
        LEFT_HAND: "Left Handed",
        RIGHT_HAND: "Right Handed",
    }

    name = models.CharField(max_length=100, blank=False)
    born = models.DateTimeField(blank=True, null=True)
    country = models.ForeignKey(Country, null=True, on_delete=models.PROTECT)
    player_skill = models.IntegerField(null=True, blank=True, choices=skill_choices)
    player_hand = models.IntegerField(
        null=False, default=RIGHT_HAND, choices=hands_choices
    )

    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

    def team(self, match_or_tournament):
        if isinstance(match_or_tournament, Match):
            t = match_or_tournament.tournament
        else:
            t = match_or_tournament

        th = PlayerTournamentHistory.objects.get(player=self, tournament=t)
        return th.team

    def skill(self):
        for skill_id, skill in self.skill_choices:
            if skill_id == self.player_skill:
                return skill

    def tournament_skill(self, tournament):
        return PlayerTournamentHistory.objects.get(
            player=self, tournament=tournament
        ).player_skill

    def hand(self):
        for hand_id, hand in self.hands_choices:
            if hand_id == self.player_hand:
                return hand


class Team(models.Model):
    name = models.CharField(max_length=100, blank=False)
    abbreviation = models.CharField(max_length=20, blank=False, default="", null=False)
    country = models.ForeignKey(Country, null=True, on_delete=models.PROTECT)
    fake_team = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

    def match_tournament_players(self, tournament, match):
        player_format_attr = match.MatchTypeToPTHAttrMapping[match.match_type]

        filters = {
            "team": self,
            player_format_attr: True,
            "tournament": tournament,
        }

        return [
            tph.player
            for tph in PlayerTournamentHistory.objects.filter(**filters)
            .order_by("player__name")
            .exclude(
                status__in=(
                    PlayerTournamentHistory.PLAYER_WITHDRAWN,
                    PlayerTournamentHistory.PLAYER_NOT_PLAYING_MATCHES,
                )
            )
            .all()
        ]

    def tournament_players(self, tournament):
        filters = {
            "team": self,
            "tournament": tournament,
        }

        return [
            tph.player
            for tph in PlayerTournamentHistory.objects.filter(**filters)
            .order_by("player__name")
            .exclude(status=PlayerTournamentHistory.PLAYER_WITHDRAWN)
            .all()
        ]


# live_score changes: Squad should be renamed to TournamentTeam
class Squad(models.Model):
    squad_number = models.IntegerField(blank=False, null=False)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, on_delete=models.PROTECT)
    players = models.ManyToManyField(Player, blank=True)
    matches_played = models.CharField(
        max_length=100, null=False, blank=False, default="Not Played"
    )

    def update_matches_played(self):
        match = None
        if self.match_team_one.count() == 1:
            match = self.match_team_one.get()
        elif self.match_team_two.count() == 1:
            match = self.match_team_two.get()

        if match:
            self.matches_played = "Match: [{}, {}]".format(
                match.tournament, match.match_number
            )
            super(Squad, self).save()

    def __str__(self):
        return "{} -- {}, squad: {}".format(
            self.matches_played, self.team.name, self.squad_number
        )


class Match(models.Model):
    # Match Types
    ONE_DAY = 1
    T_TWENTY = 2
    TEST = 3

    # Match Outcomes
    LIVE = 1
    COMPLETED = 2
    SCHEDULED = 3

    # Toss Decisions
    BAT = 1
    FIELD = 2
    BOWL = 2

    # Toss Outcomes
    HEADS = 1
    TAILS = 2
    UNKNOWN = 3

    # Match results
    MR_UNKNOWN = -1
    MR_WIN = 0
    MR_TIE = 1
    MR_DRAW = 2
    MR_NO_RESULT = 3
    MR_ABANDONED = 4

    match_types = ((ONE_DAY, "One Day"), (T_TWENTY, "T-20"), (TEST, "Test match"))

    match_statuses = (
        (COMPLETED, "Completed"),
        (SCHEDULED, "Scheduled"),
        (LIVE, "Live"),
    )

    match_results = (
        (MR_UNKNOWN, "Unknown"),
        (MR_WIN, "Win"),
        (MR_TIE, "Tie"),
        (MR_DRAW, "Draw"),
        (MR_NO_RESULT, "No Result"),
        (MR_ABANDONED, "Abandoned"),
    )

    MatchTypeToPTHAttrMapping = {
        T_TWENTY: "t20_player",
        ONE_DAY: "odi_player",
        TEST: "test_player",
    }

    toss_decisions = ((BAT, "Bat"), (BOWL, "Bowl"), (FIELD, "Field"))

    toss_outcomes = ((HEADS, "Heads"), (TAILS, "Tails"), (UNKNOWN, "Unknown"))

    name = models.CharField(max_length=200, blank=True, null=False)
    tournament = models.ForeignKey(
        Tournament, on_delete=models.PROTECT, related_name="matches"
    )
    venue = models.ForeignKey(Venue, null=True, blank=True, on_delete=models.PROTECT)
    match_date = models.DateTimeField(blank=False, null=False)
    match_number = models.IntegerField(blank=False, null=False)
    match_type = models.IntegerField(null=False, blank=False, choices=match_types)
    match_status = models.IntegerField(null=False, blank=False, choices=match_statuses)
    match_result = models.IntegerField(
        default=MR_UNKNOWN, null=False, blank=False, choices=match_results
    )
    team_one = models.ForeignKey(
        Squad,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="match_team_one",
    )

    team_two = models.ForeignKey(
        Squad,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="match_team_two",
    )
    first_innings_runs = models.IntegerField(blank=False, null=False, default=0)
    first_innings_balls = models.IntegerField(blank=False, null=False, default=0)
    second_innings_runs = models.IntegerField(blank=False, null=False, default=0)
    second_innings_balls = models.IntegerField(blank=False, null=False, default=6)
    maximum_overs = models.IntegerField(blank=False, null=False, default=20)
    available_overs = models.IntegerField(blank=False, null=False, default=20)
    first_innings_overs = models.IntegerField(blank=False, null=False, default=0)
    second_innings_overs = models.IntegerField(blank=False, null=False, default=0)
    calculated_winning_score = models.IntegerField(blank=False, null=False, default=0)
    winning_score = models.IntegerField(blank=True, null=False, default=0)
    first_innings_wickets = models.IntegerField(blank=True, null=False, default=0)
    second_innings_wickets = models.IntegerField(blank=True, null=False, default=0)
    bat_first_team = models.ForeignKey(
        Squad, on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    winning_team = models.ForeignKey(
        Squad, on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    toss_winner = models.ForeignKey(
        Squad, on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    toss_outcome = models.IntegerField(
        blank=True, null=True, choices=toss_outcomes, default=UNKNOWN
    )
    toss_decision = models.IntegerField(blank=True, null=True, choices=toss_decisions)
    toss_time = models.DateTimeField(blank=True, null=True)
    match_start_time = models.DateTimeField(blank=True, null=True)
    super_over_played = models.BooleanField(default=False, blank=True, null=False)
    super_over_winner = models.ForeignKey(
        Squad, on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )

    first_innings_fours = models.IntegerField(blank=False, null=False, default=0)
    first_innings_sixes = models.IntegerField(blank=False, null=False, default=0)
    first_innings_extras = models.IntegerField(blank=False, null=False, default=0)
    first_innings_noballs = models.IntegerField(blank=False, null=False, default=0)
    first_innings_wides = models.IntegerField(blank=False, null=False, default=0)
    first_innings_byes = models.IntegerField(blank=False, null=False, default=0)
    first_innings_legbyes = models.IntegerField(blank=False, null=False, default=0)
    first_innings_penalties = models.IntegerField(blank=False, null=False, default=0)
    first_innings_catches = models.IntegerField(blank=False, null=False, default=0)
    first_innings_stumpings = models.IntegerField(blank=False, null=False, default=0)
    first_innings_runouts = models.IntegerField(blank=False, null=False, default=0)
    first_innings_free_hits = models.IntegerField(blank=False, null=False, default=0)
    first_innings_bowled = models.IntegerField(blank=False, null=False, default=0)
    first_innings_lbws = models.IntegerField(blank=False, null=False, default=0)

    second_innings_free_hits = models.IntegerField(blank=False, null=False, default=0)
    second_innings_bowled = models.IntegerField(blank=False, null=False, default=0)
    second_innings_lbws = models.IntegerField(blank=False, null=False, default=0)
    second_innings_fours = models.IntegerField(blank=False, null=False, default=0)
    second_innings_sixes = models.IntegerField(blank=False, null=False, default=0)
    second_innings_extras = models.IntegerField(blank=False, null=False, default=0)
    second_innings_noballs = models.IntegerField(blank=False, null=False, default=0)
    second_innings_wides = models.IntegerField(blank=False, null=False, default=0)
    second_innings_byes = models.IntegerField(blank=False, null=False, default=0)
    second_innings_legbyes = models.IntegerField(blank=False, null=False, default=0)
    second_innings_penalties = models.IntegerField(blank=False, null=False, default=0)
    second_innings_catches = models.IntegerField(blank=False, null=False, default=0)
    second_innings_stumpings = models.IntegerField(blank=False, null=False, default=0)
    second_innings_runouts = models.IntegerField(blank=False, null=False, default=0)

    third_innings_runs = models.IntegerField(blank=False, null=False, default=0)
    third_innings_wickets = models.IntegerField(blank=False, null=False, default=0)
    third_innings_overs = models.IntegerField(blank=False, null=False, default=0)
    third_innings_balls = models.IntegerField(blank=False, null=False, default=0)
    third_innings_free_hits = models.IntegerField(blank=False, null=False, default=0)
    third_innings_bowled = models.IntegerField(blank=False, null=False, default=0)
    third_innings_lbws = models.IntegerField(blank=False, null=False, default=0)
    third_innings_fours = models.IntegerField(blank=False, null=False, default=0)
    third_innings_sixes = models.IntegerField(blank=False, null=False, default=0)
    third_innings_extras = models.IntegerField(blank=False, null=False, default=0)
    third_innings_noballs = models.IntegerField(blank=False, null=False, default=0)
    third_innings_wides = models.IntegerField(blank=False, null=False, default=0)
    third_innings_byes = models.IntegerField(blank=False, null=False, default=0)
    third_innings_legbyes = models.IntegerField(blank=False, null=False, default=0)
    third_innings_penalties = models.IntegerField(blank=False, null=False, default=0)
    third_innings_catches = models.IntegerField(blank=False, null=False, default=0)
    third_innings_stumpings = models.IntegerField(blank=False, null=False, default=0)
    third_innings_runouts = models.IntegerField(blank=False, null=False, default=0)

    fourth_innings_runs = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_wickets = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_overs = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_balls = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_free_hits = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_bowled = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_lbws = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_fours = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_sixes = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_extras = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_noballs = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_wides = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_byes = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_legbyes = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_penalties = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_catches = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_stumpings = models.IntegerField(blank=False, null=False, default=0)
    fourth_innings_runouts = models.IntegerField(blank=False, null=False, default=0)

    maximum_overs_balls = models.IntegerField(blank=False, null=False, default=0)
    final_overs = models.IntegerField(blank=False, null=False, default=20)
    final_overs_balls = models.IntegerField(blank=False, null=False, default=0)
    bonus_value = models.FloatField(blank=False, null=False, default=0.0)
    bonus_applicable = models.BooleanField(blank=False, null=False, default=False)
    final_winning_score = models.IntegerField(blank=False, null=False, default=0)
    max_fours_by = models.ManyToManyField(Player, blank=True, related_name="+")
    max_sixes_by = models.ManyToManyField(Player, blank=True, related_name="+")
    most_runs_by = models.ManyToManyField(Player, blank=True, related_name="+")
    most_wickets_by = models.ManyToManyField(Player, blank=True, related_name="+")

    submissions_allowed = models.BooleanField(blank=False, null=False, default=False)

    win_margin_runs = models.IntegerField(blank=True, null=True)

    first_wicket_gone_in_over = models.IntegerField(blank=True, null=True)

    dl_applicable = models.BooleanField(blank=True, null=False, default=False)
    dl_overs = models.IntegerField(blank=True, null=True, default=0)
    dl_overs_balls = models.IntegerField(blank=True, null=True, default=0)
    dl_target = models.IntegerField(blank=True, null=True, default=0)
    dl_calculated_winning_score = models.IntegerField(blank=True, null=True, default=0)
    reference_name = models.CharField(max_length=100, blank=True, null=False)
    post_toss_changes_allowed = models.BooleanField(
        null=False, default=False, blank=False
    )
    short_display_name = models.CharField(max_length=100, null=True, blank=True)

    fake_match = models.BooleanField(null=False, default=False, blank=False)

    class Meta:
        unique_together = (("tournament", "id", "name"),)
        verbose_name_plural = "matches"

    def assign_scores(self):
        # Start off with False
        self.bonus_applicable = False

        # Bonus Applicable
        if self.winning_team == self.bat_first_team:
            self.bonus_value = self.first_innings_runs / 1.25
        else:
            self.bonus_value = (self.final_overs + (self.final_overs_balls / 6)) / 1.25

        if (self.winning_team == self.bat_first_team) and (
            self.second_innings_runs <= self.bonus_value
        ):

            self.bonus_applicable = True

        if (self.winning_team != self.bat_first_team) and (
            self.second_innings_overs + (self.second_innings_balls / 6)
            <= self.bonus_value
        ):

            self.bonus_applicable = True

        # DL overries everything
        if self.dl_applicable:
            if self.winning_team == self.bat_first_team:
                self.bonus_value = self.dl_calculated_winning_score / 1.25

                if self.second_innings_runs <= self.bonus_value:
                    self.bonus_applicable = True
                else:
                    self.bonus_applicable = False
            else:
                self.bonus_value = (self.dl_overs + (self.dl_overs_balls / 6)) / 1.25

                if (
                    self.second_innings_overs + (self.second_innings_balls / 6)
                    <= self.bonus_value
                ):
                    self.bonus_applicable = True
                else:
                    self.bonus_applicable = False

        # Calculated Winning Score
        if self.winning_team == self.bat_first_team:
            self.winning_score = self.first_innings_runs
            self.calculated_winning_score = self.first_innings_runs
            self.final_winning_score = self.first_innings_runs

        else:
            self.winning_score = self.second_innings_runs
            self.calculated_winning_score = round(
                (
                    self.second_innings_runs
                    / (self.second_innings_overs + (self.second_innings_balls / 6))
                )
                * (self.maximum_overs + self.maximum_overs_balls / 6)
            )

            # Final Winning Score
            self.final_winning_score = round(
                (
                    self.second_innings_runs
                    / (self.second_innings_overs + (self.second_innings_balls / 6))
                    * (self.final_overs + self.final_overs_balls / 6)
                )
            )

    def assign_dl_scores(self):
        if self.dl_applicable:
            self.dl_calculated_winning_score = self.dl_target - 1

    def save(self, *args, **kwargs):
        if self.team_one and self.team_two:
            if self.match_result != Match.MR_ABANDONED:
                self.assign_dl_scores()
                self.assign_scores()

        super(Match, self).save(*args, **kwargs)

    def assign_short_display_name(self):
        if not self.fake_match:
            if self.team_one and self.team_two:
                namer = eval(self.tournament.short_display_name_strategy, {})
                self.short_display_name = namer(self)
            else:
                self.short_display_name = "{}, {}: TBC vs. TBC".format(
                    self.tournament.name, self.reference_name
                )

        super(Match, self).save()

    def assign_name(self):
        if not self.fake_match:
            if self.team_one and self.team_two:
                namer = eval(self.tournament.match_naming_strategy, {})
                self.name = namer(self)
            else:
                self.name = "{}: TBC vs. TBC".format(self.reference_name)

        super(Match, self).save()

    def teams_only_name(self):
        if not self.fake_match:
            if self.team_one and self.team_two:
                return f"{self.team_one.team.name} vs. {self.team_two.team.name}"
            else:
                return "{}: TBC vs. TBC".format(self.reference_name)

    def __str__(self):
        if self.team_one and self.team_two:
            return "{}, {}: {} vs. {}".format(
                self.tournament.name,
                self.reference_name,
                self.team_one.team.name,
                self.team_two.team.name,
            )
        else:
            return "{}, {}: TBC vs. TBC".format(self.tournament, self.reference_name)

    def teams(self):
        t = []

        if self.team_one:
            t.append(self.team_one.team)

        if self.team_two:
            t.append(self.team_two.team)

        return t

    def squads(self):
        return [self.team_one, self.team_two]

    def tournament_players(self):
        players = []

        if self.team_one.team:
            players.extend(
                self.team_one.team.match_tournament_players(self.tournament, self)
            )
        if self.team_two.team:
            players.extend(
                self.team_two.team.match_tournament_players(self.tournament, self)
            )

        return players

    def squad_players(self):
        players = []
        for squad in self.squads():
            players.extend(squad.players.order_by("name").all())

        return players

    def playing_eleven(self):
        return self.squad_players()

    def not_in_playing_eleven(self):
        return set(self.tournament_players()).difference(set(self.playing_eleven()))

    def start_time_utc(self):
        if self.match_date:
            return arrow.get(self.match_date).format("dddd DD/MM/YYYY h:mm A")

    def start_time_ist(self):
        if self.match_date:
            return (
                arrow.get(self.match_date)
                .to("Asia/Kolkata")
                .format("dddd DD/MM/YYYY h:mm A")
            )

    def start_time_bst(self):
        if self.match_date:
            return (
                arrow.get(self.match_date)
                .to("Europe/London")
                .format("dddd DD/MM/YYYY h:mm A")
            )

    def local_start_time(self):
        i = self.tournament.host_country.timezones.count()
        if i == 1:
            return (
                arrow.get(self.match_date)
                .to("{}".format(self.tournament.host_country.timezones.first().tz.zone))
                .format("dddd DD/MM/YYYY h:mm A")
            )
        elif i > 1:
            if self.venue and self.venue.city.timezone:
                return (
                    arrow.get(self.match_date)
                    .to("{}".format(self.venue.city.timezone.tz.zone))
                    .format("dddd DD/MM/YYYY h:mm A")
                )
            else:
                return self.start_time_utc()
        else:
            raise Exception(
                "Incorrect or missing zone for {}.".format(self.tournament.host_country)
            )

    def team_first_innings_runs(self, team):
        if team == self.bat_first_team.team:
            return self.first_innings_runs
        else:
            return self.second_innings_runs

    def submission_status(self):
        status_str = "Closed"

        if self.submissions_allowed:
            status_str = "Open"

        if self.post_toss_changes_allowed:
            status_str = "Post Toss"

        return {
            "id": self.id,
            "submission_status": status_str,
            "start_time_utc": self.start_time_utc(),
        }

    def assign_final_scores_match_name(self):
        from sportappsite.constants import MatchTypes

        if self.fake_match:

            if self.tournament.bi_lateral:
                t_str = MatchTypes.type_to_series_str(self.match_type)
                new_name = f"Final Scores ({t_str}): pre-Tournament Predictions + Match Predictions"
                new_sdn = f"Final Scores ({t_str})"
                self.name = new_name
                self.short_display_name = new_sdn

            else:
                new_name = (
                    f"Final Scores: pre-Tournament Predictions + Match Predictions"
                )
                new_sdn = f"Final Scores"
                self.name = new_name
                self.short_display_name = new_sdn

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)


# live_score changes: Adding class PlayingSquad, PlayerSquadInfo
class PlayingSquad(models.Model):
    playing_squad_number = models.IntegerField(blank=False, null=False)
    match = models.ForeignKey(Match, on_delete=models.PROTECT)
    team_tournament = models.ForeignKey(Squad, on_delete=models.PROTECT)
    players = models.ManyToManyField(Player, through="PlayerSquadInfo", blank=True)

    def display_players(self):
        return ", ".join([player.name for player in self.players.all()])

    def __str__(self):
        return "done"

    def __unicode__(self):
        return


class PlayerSquadInfo(models.Model):
    ALLROUNDER = 0
    BATSMAN = 1
    BOWLER = 2
    KEEPER = 3

    CAPTAIN = 1
    KEEPER = 2

    skill_choices = (
        (ALLROUNDER, "All Rounder"),
        (BATSMAN, "Batsman"),
        (BOWLER, "Bowler"),
        (KEEPER, "Keeper"),
    )

    role_choices = ((CAPTAIN, "Captain"), (KEEPER, "Keeper"))

    player_skill = models.IntegerField(null=True, blank=True, choices=skill_choices)
    player_role = models.IntegerField(null=True, blank=True, choices=role_choices)
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    playingSquad = models.ForeignKey(PlayingSquad, on_delete=models.PROTECT)

    def __str__(self):
        return

    def __unicode__(self):
        return


class PlayerTournamentHistory(models.Model):
    PLAYER_ACTIVE = 1
    PLAYER_WITHDRAWN = 2
    PLAYER_NOT_PLAYING_MATCHES = 3

    ALLROUNDER = 0
    BATSMAN = 1
    BOWLER = 2
    KEEPER = 3

    skill_choices = (
        (ALLROUNDER, "All-rounder"),
        (BATSMAN, "Batsman"),
        (BOWLER, "Bowler"),
        (KEEPER, "Wicket-keeper"),
    )

    status_choices = (
        (PLAYER_ACTIVE, "Active"),
        (PLAYER_WITHDRAWN, "Withdrawn"),
        (PLAYER_NOT_PLAYING_MATCHES, "Not playing Matches"),
    )
    player = models.ForeignKey(
        Player, null=False, blank=False, on_delete=models.PROTECT
    )
    tournament = models.ForeignKey(
        Tournament, null=False, blank=False, on_delete=models.PROTECT
    )
    team = models.ForeignKey(Team, null=False, blank=False, on_delete=models.PROTECT)
    status = models.IntegerField(
        blank=False, default=PLAYER_ACTIVE, choices=status_choices
    )
    date_withdrawn = models.DateField(null=True, blank=True)
    player_skill = models.IntegerField(null=True, blank=True, choices=skill_choices)
    is_captain = models.BooleanField(null=False, default=False)
    is_vice_captain = models.BooleanField(null=False, default=False)
    jersey_number = models.IntegerField(null=False, default=0, blank=False)
    test_player = models.BooleanField(null=False, default=False,)
    odi_player = models.BooleanField(null=False, default=False,)
    t20_player = models.BooleanField(null=False, default=False,)
    test_captain = models.BooleanField(null=False, default=False,)
    odi_captain = models.BooleanField(null=False, default=False,)
    t20_captain = models.BooleanField(null=False, default=False,)
    test_vice_captain = models.BooleanField(null=False, default=False,)
    odi_vice_captain = models.BooleanField(null=False, default=False,)
    t20_vice_captain = models.BooleanField(null=False, default=False,)

    class Meta:
        unique_together = ("player", "tournament")
        verbose_name_plural = "Player Tournament histories"

    def __str__(self):
        return "{}, {}".format(self.tournament.name, self.player.name)

    @classmethod
    def player_tournament_team(cls, player, tournament):
        return cls.objects.get(player=player, tournament=tournament).team


class TournamentDefaultRules(models.Model):

    METHOD_TO_ATTR_MAP = {
        PlayerScoringMethod: "tournament_player_scoring_method",
        PredictionScoringMethod: "tournament_prediction_scoring_method",
        PredictionSubmissionValidationRule: "tournament_prediction_validation_rules",
        PostMatchPredictionScoringMethod: "tournament_post_predictions_scoring_methods",
        LeaderBoardScoringMethod: "tournament_leaderboard_scoring_methods",
        TournamentScoringMethod: None,
    }

    tournament = models.ForeignKey(
        Tournament, null=False, blank=False, on_delete=models.PROTECT
    )
    tournament_player_scoring_method = models.ManyToManyField(
        PlayerScoringMethod, blank=True
    )
    tournament_prediction_scoring_method = models.ManyToManyField(
        PredictionScoringMethod, blank=True
    )
    tournament_prediction_validation_rules = models.ManyToManyField(
        PredictionSubmissionValidationRule, blank=True
    )
    tournament_post_predictions_scoring_methods = models.ManyToManyField(
        PostMatchPredictionScoringMethod, blank=True
    )
    tournament_leaderboard_scoring_methods = models.ManyToManyField(
        LeaderBoardScoringMethod, blank=True
    )

    def __str__(self):
        return "Default Rules for:  {}".format(self.tournament.name)

    def rules(self):
        return (
            list(self.tournament_player_scoring_method.all())
            + list(self.tournament_prediction_scoring_method.all())
            + list(self.tournament_prediction_validation_rules.all())
            + list(self.tournament_post_predictions_scoring_methods.all())
            + list(self.tournament_leaderboard_scoring_methods.all())
        )

    class Meta:
        verbose_name_plural = "Tournament Default Rules"


reversion.register(Tournament)
reversion.register(Country)
reversion.register(City)
reversion.register(Team)
reversion.register(Venue)
reversion.register(Squad)
reversion.register(Match)
reversion.register(Player)
reversion.register(PlayerTournamentHistory)
reversion.register(TournamentDefaultRules)
