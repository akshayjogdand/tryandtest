from django.db import models

from reversion import revisions as reversion

from python_field.python_field import PythonCodeField

from fixtures.models import Match, Player, Team, Tournament

from rules.models import PlayerScoringResult

from members.models import MemberGroup


class BowlingPerformance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    match = models.ForeignKey(Match, on_delete=models.PROTECT)
    innings = models.IntegerField(default=1, null=False, blank=False)
    team = models.ForeignKey(Team, null=False, blank=False, on_delete=models.PROTECT)
    overs = models.IntegerField(null=False, blank=False, default=0)
    balls = models.IntegerField(null=False, blank=False, default=0)
    maiden = models.IntegerField(null=False, blank=False, default=0)
    runs = models.IntegerField(null=False, blank=False, default=0)
    wickets = models.IntegerField(null=False, blank=False, default=0)
    extras = models.IntegerField(null=False, blank=False, default=0)
    dot_balls = models.IntegerField(null=False, blank=False, default=0)
    fours = models.IntegerField(null=False, blank=False, default=0)
    sixes = models.IntegerField(null=False, blank=False, default=0)
    hat_tricks = models.IntegerField(null=False, blank=False, default=0)
    economy = models.FloatField(null=False, blank=True, default=0.00)
    is_maiden = models.BooleanField(null=False, default=False)
    hattrick_count = models.IntegerField(null=False, default=0)

    class Meta:
        unique_together = ("player", "match", "innings")

    def save(self, *args, **kwargs):
        if self.overs == 0 and self.balls == 0:
            self.economy = 0.00
        else:
            self.economy = round(
                (self.runs + self.extras) / (self.overs + (self.balls / 6)), 2
            )

        super(BowlingPerformance, self).save(*args, **kwargs)

    def __str__(self):
        return "Bowling stats: {} for {} in {}".format(
            self.player, self.team, self.match
        )


class BattingPerformance(models.Model):

    # Dismissals
    BOWLED = 1
    CAUGHT = 2
    NOT_OUT = 3
    RETIRED_HURT = 4
    TIMED_OUT = 5
    HANDLED = 6
    HIT_TWICE = 7
    HIT_WICKET = 8
    LBW = 9
    OBSTRUCTING_FIELD = 10
    STUMPED = 11
    RUN_OUT = 12
    ABSENT_HURT = 13

    # was_out
    WO_UNKNOWN = 0
    WO_OUT = 1
    WO_NOT_OUT = 2
    WO_DNB = 3

    dismissals_choices = (
        (BOWLED, "Bowled"),
        (CAUGHT, "Caught"),
        (NOT_OUT, "Not Out"),
        (RETIRED_HURT, "Retired Hurt"),
        (TIMED_OUT, "Timed Out"),
        (HANDLED, "Handled"),
        (HIT_TWICE, "Hit Twice"),
        (HIT_WICKET, "Hit Wicket"),
        (LBW, "LBW"),
        (OBSTRUCTING_FIELD, "Obstructing Field"),
        (STUMPED, "Stumped"),
        (RUN_OUT, "Run Out"),
        (ABSENT_HURT, "Absent Hurt"),
    )

    was_out_choices = (
        (WO_UNKNOWN, "Unknown"),
        (WO_OUT, "Out"),
        (WO_NOT_OUT, "Not Out"),
        (WO_DNB, "Did Not Bat"),
    )

    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    match = models.ForeignKey(Match, on_delete=models.PROTECT)
    innings = models.IntegerField(default=1, null=False, blank=False)
    team = models.ForeignKey(Team, null=False, blank=False, on_delete=models.PROTECT)
    position = models.IntegerField(null=False, blank=False, default=0)
    runs = models.IntegerField(null=False, blank=False, default=0)
    balls = models.IntegerField(null=False, blank=False, default=0)
    zeros = models.IntegerField(null=False, blank=False, default=0)
    ones = models.IntegerField(null=False, blank=False, default=0)
    twos = models.IntegerField(null=False, blank=False, default=0)
    threes = models.IntegerField(null=False, blank=False, default=0)
    fours = models.IntegerField(null=False, blank=False, default=0)
    fives = models.IntegerField(null=False, blank=False, default=0)
    sixes = models.IntegerField(null=False, blank=False, default=0)
    seven_plus = models.IntegerField(null=False, blank=False, default=0)
    was_out = models.IntegerField(
        blank=False, null=False, default=WO_UNKNOWN, choices=was_out_choices
    )
    strike_rate = models.FloatField(null=False, blank=True, default=0.00)
    dismissal = models.IntegerField(blank=True, null=True, choices=dismissals_choices)
    fielder = models.ManyToManyField(Player, blank=True, related_name="+")
    bowler = models.ForeignKey(
        Player, on_delete=models.PROTECT, blank=True, null=True, related_name="bowler"
    )
    fall_of_wicket_score = models.IntegerField(null=True, blank=True)
    wicket_number = models.IntegerField(null=True, blank=True)
    not_out_batsman = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="not_out_batsman",
    )
    not_out_batsman_score = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("player", "match", "innings")

    def save(self, *args, **kwargs):
        if self.balls == 0:
            self.strike_rate = 0.00
        else:
            self.strike_rate = round((self.runs / self.balls) * 100, 2)

        super(BattingPerformance, self).save(*args, **kwargs)

    def __str__(self):
        return "Batting stats: {} for {} in {}".format(
            self.player, self.team, self.match
        )


class FieldingPerformance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    match = models.ForeignKey(Match, on_delete=models.PROTECT)
    innings = models.IntegerField(default=1, null=False, blank=False)
    team = models.ForeignKey(Team, null=False, blank=False, on_delete=models.PROTECT)
    catches = models.IntegerField(null=False, blank=False, default=0)
    stumpings = models.IntegerField(null=False, blank=False, default=0)
    runouts = models.IntegerField(null=False, blank=False, default=0)

    class Meta:
        unique_together = ("player", "match", "innings")

    def __str__(self):
        return "Fielding stats: {} for {} in {}".format(
            self.player, self.team, self.match
        )


class MatchPerformance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    match = models.ForeignKey(Match, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, null=False, blank=False, on_delete=models.PROTECT)
    last_run = models.BooleanField(null=False, default=False)
    last_wicket = models.BooleanField(null=False, default=False)
    man_of_the_match = models.BooleanField(null=False, default=False)
    max_fours_hit = models.BooleanField(null=False, default=False)
    max_sixes_hit = models.BooleanField(null=False, default=False)
    is_captain = models.BooleanField(null=False, default=False)
    is_wicketkeeper = models.BooleanField(null=False, default=False)
    most_runs = models.BooleanField(null=False, default=False)
    most_wickets = models.BooleanField(null=False, default=False)

    class Meta:
        unique_together = ("player", "match")

    def __str__(self):
        return "Match Performance: {} for {} in {}".format(
            self.player, self.team, self.match
        )


class PlayerScores(models.Model):
    player = models.ForeignKey(
        Player, null=False, blank=False, on_delete=models.PROTECT
    )
    match = models.ForeignKey(Match, null=False, blank=False, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, null=False, blank=False, on_delete=models.PROTECT)
    scored_on = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    total_score = models.FloatField(null=False, blank=False, default=0.00)
    detailed_scoring = models.ManyToManyField(
        PlayerScoringResult, related_name="match_player_scoring_results"
    )

    class Meta:
        verbose_name_plural = "Player scores"
        unique_together = ("player", "match")

    def __str__(self):
        return "{}, {}, match-{} [{}]".format(
            self.player.name,
            self.match.tournament.name,
            self.match.match_number,
            self.total_score,
        )


class PlayerStat(models.Model):
    # Match Types
    ONE_DAY = 1
    T_TWENTY = 2
    TEST = 3

    match_types = ((ONE_DAY, "One Day"), (T_TWENTY, "T-20"), (TEST, "Test match"))

    stat_name = models.CharField(max_length=100, null=False, blank=False)
    stat_value = models.FloatField(null=False, default=0.0, blank=False)
    stat_unit = models.IntegerField(null=True, blank=True)
    stat_index = models.IntegerField(null=True)
    player = models.ForeignKey(
        Player, null=False, blank=False, on_delete=models.PROTECT
    )
    match = models.ForeignKey(Match, null=True, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, null=False, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.PROTECT)
    match_or_tournament_format = models.IntegerField(
        null=True, blank=True, choices=match_types
    )
    member_group = models.ForeignKey(
        MemberGroup, null=True, blank=True, on_delete=models.PROTECT
    )

    calculation = PythonCodeField(max_length=200, null=True, blank=True)
    computed_on = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    is_latest = models.BooleanField(null=False, default=False, blank=False)
    add_counter = models.IntegerField(null=False, default=0, blank=False)
    removed_counter = models.IntegerField(null=False, default=0, blank=False)
    submission_count = models.IntegerField(null=False, blank=False, default=0)

    def inc(self):
        self.add_counter = self.add_counter + 1

    def dec(self):
        self.removed_counter = self.removed_counter + 1

    def total(self):
        return self.add_counter - self.removed_counter

    def __str__(self):
        if self.match:
            tournament = ""
            if self.tournament and self.tournament.name:
                tournament = self.tournament.name
            return "{}, {}, {}, match-{} [{}]".format(
                self.stat_name,
                self.player.name,
                tournament,
                self.match.match_number,
                self.stat_value,
            )
        else:
            return "{}, {}, match-{} [{}]".format(
                self.stat_name, self.player.name, self.tournament.name, self.stat_value
            )


class TeamStat(models.Model):
    # Match Types
    ONE_DAY = 1
    T_TWENTY = 2
    TEST = 3

    match_types = ((ONE_DAY, "One Day"), (T_TWENTY, "T-20"), (TEST, "Test match"))

    stat_name = models.CharField(max_length=100, null=False, blank=False)
    stat_value = models.FloatField(null=False, default=0.0, blank=False)
    stat_unit = models.IntegerField(null=True, blank=True)
    stat_index = models.IntegerField(null=True)
    match = models.ForeignKey(Match, null=True, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, null=False, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.PROTECT)
    match_or_tournament_format = models.IntegerField(
        null=True, blank=True, choices=match_types
    )
    member_group = models.ForeignKey(
        MemberGroup, null=True, blank=True, on_delete=models.PROTECT
    )

    calculation = PythonCodeField(max_length=200, null=True, blank=True)
    computed_on = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    is_latest = models.BooleanField(null=False, default=False, blank=False)
    add_counter = models.IntegerField(null=False, default=0, blank=False)
    removed_counter = models.IntegerField(null=False, default=0, blank=False)
    submission_count = models.IntegerField(null=False, blank=False, default=0)

    def inc(self):
        self.add_counter = self.add_counter + 1

    def dec(self):
        self.removed_counter = self.removed_counter + 1

    def total(self):
        return self.add_counter - self.removed_counter

    def __str__(self):
        if self.match:
            t = self.match.name
        elif self.tournament:
            t = self.tournament.name

        return "{}, {}, {}, [{}]".format(
            self.stat_name, self.team.name, t, self.stat_value,
        )


class PredictionFieldStat(models.Model):
    # Match Types
    ONE_DAY = 1
    T_TWENTY = 2
    TEST = 3

    match_types = ((ONE_DAY, "One Day"), (T_TWENTY, "T-20"), (TEST, "Test match"))

    stat_name = models.CharField(max_length=100, null=False, blank=False)
    stat_value = models.FloatField(null=False, default=0.0, blank=False)
    stat_unit = models.IntegerField(null=True, blank=True)
    stat_index = models.IntegerField(null=True)
    match_or_tournament_format = models.IntegerField(
        null=True, blank=True, choices=match_types
    )
    match = models.ForeignKey(Match, null=True, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, null=True, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.PROTECT)
    member_group = models.ForeignKey(
        MemberGroup, null=True, blank=True, on_delete=models.PROTECT
    )

    calculation = PythonCodeField(max_length=200, null=True, blank=True)
    computed_on = models.DateTimeField(null=False, blank=True, auto_now_add=True)
    is_latest = models.BooleanField(null=False, default=False, blank=False)
    add_counter = models.IntegerField(null=False, default=0, blank=False)
    removed_counter = models.IntegerField(null=False, default=0, blank=False)
    raw_input_value = models.IntegerField(null=True, blank=True)
    submission_count = models.IntegerField(null=False, blank=False, default=0)

    def inc(self):
        self.add_counter = self.add_counter + 1

    def dec(self):
        self.removed_counter = self.removed_counter + 1

    def total(self):
        return self.add_counter - self.removed_counter

    def __str__(self):
        if self.match:
            game = self.match.name
        else:
            game = self.tournament

        return "{}, {}, {}, {}".format(game, self.id, self.stat_name, self.stat_value,)


reversion.register(BowlingPerformance)
reversion.register(BattingPerformance)
reversion.register(FieldingPerformance)
reversion.register(MatchPerformance)
reversion.register(PlayerScores)
reversion.register(TeamStat)
reversion.register(PlayerStat)
reversion.register(PredictionFieldStat)
