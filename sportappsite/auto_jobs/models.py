from django.db import models

from django.utils import timezone

from python_field.python_field import PythonCodeField

from python_field.utils import is_dict

from fixtures.models import Match, Tournament, Player, TournamentFormats, Team


class AutoJob(models.Model):
    STATE_ATTRS = []

    execute = models.BooleanField(default=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    job_refs = models.TextField(blank=True)

    class Meta:
        abstract = True

    def state_string(self, job_id):
        states = []
        for a in self.STATE_ATTRS:
            v = getattr(self, a)
            states.append(f"{a}={v}")

        return f"Job ID={job_id} ts={timezone.now()} {states}"


class FetchSeries(AutoJob):
    series_key = models.CharField(max_length=20, blank=False, null=False, unique=True)
    pull_data = models.BooleanField(default=False, blank=False)
    adjust_tournament_data = models.BooleanField(default=False, blank=False)
    add_to_all_groups = models.BooleanField(default=False, blank=False)

    STATE_ATTRS = [
        "execute",
        "pull_data",
        "adjust_tournament_data",
        "add_to_all_groups",
    ]

    class Meta:
        verbose_name_plural = "Fetch Series Jobs"
        verbose_name = "Fetch Series Job"

    def __str__(self):
        return f"Fetch Series: {self.series_key}"

    def reset_job(self):
        self.execute = False
        self.pull_data = False
        self.adjust_tournament_data = False
        self.add_to_all_groups = False


class ScoreMatch(AutoJob):
    match = models.OneToOneField(
        Match, null=False, on_delete=models.PROTECT, unique=True
    )
    fetch_scores = models.BooleanField(default=False, blank=False)
    convert_predictions = models.BooleanField(default=False, blank=False)
    score_players = models.BooleanField(default=False, blank=False)
    leaderboards = models.BooleanField(default=False, blank=False)
    rewards = models.BooleanField(default=False, blank=False)

    revert_prediction_conversions = models.BooleanField(default=False, blank=False)

    STATE_ATTRS = [
        "execute",
        "fetch_scores",
        "convert_predictions",
        "score_players",
        "leaderboards",
        "rewards",
        "revert_prediction_conversions",
    ]

    class Meta:
        verbose_name_plural = "Score Match Jobs"
        verbose_name = "Score Match Job"

    def __str__(self):
        return f"Score Match: {self.match}"

    def reset_job(self):
        self.execute = False
        self.fetch_scores = False
        self.convert_predictions = False
        self.score_players = False
        self.leaderboards = False
        self.rewards = False
        self.revert_prediction_conversions = False


class ScoreSeries(AutoJob):
    tournament = models.ForeignKey(Tournament, null=False, on_delete=models.PROTECT)
    convert_predictions = models.BooleanField(default=False, blank=False)
    leaderboards = models.BooleanField(default=False, blank=False)
    series = models.IntegerField(
        null=False, blank=False, choices=TournamentFormats.type_choices()
    )

    score_t20_wc = models.BooleanField(default=False, null=False, )

    win_series_margin = models.IntegerField(
        null=True,
        blank=True,
        choices=((0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)),
    )

    winner = models.ForeignKey(
        Team, null=False, on_delete=models.PROTECT, related_name="tournament_winner"
    )
    runner_up = models.ForeignKey(
        Team, null=True, blank=True, on_delete=models.PROTECT, related_name="runner_up"
    )

    team_one = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_team_one",
    )
    team_two = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_team_two",
    )
    team_three = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_team_three",
    )
    team_four = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_team_four",
    )

    last_team = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="last_team",
    )

    batsman_one = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_batsman_one",
    )
    batsman_two = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_batsman_two",
    )
    batsman_three = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_batsman_three",
    )
    batsman_four = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_batsman_four",
    )
    batsman_five = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_batsman_five",
    )

    bowler_one = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_bowler_one",
    )
    bowler_two = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_bowler_two",
    )
    bowler_three = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_bowler_three",
    )
    bowler_four = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_bowler_four",
    )
    bowler_five = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="top_bowler_five",
    )

    mvp_one = models.ForeignKey(
        Player, null=True, blank=True, on_delete=models.PROTECT, related_name="mvp_one"
    )
    mvp_two = models.ForeignKey(
        Player, null=True, blank=True, on_delete=models.PROTECT, related_name="mvp_two"
    )
    mvp_three = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="mvp_three",
    )
    mvp_four = models.ForeignKey(
        Player, null=True, blank=True, on_delete=models.PROTECT, related_name="mvp_four"
    )
    mvp_five = models.ForeignKey(
        Player, null=True, blank=True, on_delete=models.PROTECT, related_name="mvp_five"
    )

    player_of_the_tournament = models.ForeignKey(
        Player,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="player_of_the_tournament",
    )

    _BONUS_SAMPLE = """'''
Config Syntax
    [
        {
          'mg': Member Group ID,
          'members': (Member IDs,),
          'bonus': NNNN
         },
        {...}, {...}, ...
   ]
'''

[]
"""
    bonus_configuration = PythonCodeField(
        default=_BONUS_SAMPLE,
        blank=False,
        null=False,
        max_length=200,
        validators=(is_dict,),
        help_text="Ensure this ends up as a [], even if empty.",
    )

    STATE_ATTRS = ("execute", "convert_predictions", "leaderboards", "series", 'score_t20_wc')

    class Meta:
        verbose_name_plural = "Score Series Jobs"
        verbose_name = "Score Series Job"
        unique_together = ("tournament", "series")

    def __str__(self):
        return f"Score Series [{self.series}] for: {self.tournament.name}"

    def reset_job(self):
        self.execute = False
        self.convert_predictions = False
        self.leaderboards = False
        self.score_t20_wc = False
