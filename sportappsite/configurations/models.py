from django.db import models

from python_field.python_field import PythonCodeField

from python_field.utils import is_code_and_lambda

from reversion import revisions as reversion

from fixtures.models import Team, Tournament, Player, Match, TournamentFormats

from members.models import MemberGroup

from python_field.python_field import PythonCodeField


class ConfigItem(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    value = models.TextField(null=True, blank=True)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.PROTECT)
    tournament = models.ForeignKey(
        Tournament, null=True, blank=True, on_delete=models.PROTECT
    )
    player = models.ForeignKey(Player, null=True, blank=True, on_delete=models.PROTECT)
    member_group = models.ForeignKey(
        MemberGroup, null=True, blank=True, on_delete=models.PROTECT
    )
    function = PythonCodeField(null=True, blank=True, max_length=300)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Config Items"
        unique_together = ("name", "tournament")


class MatchSubmissionNotes(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    value = models.TextField(null=False, blank=False)
    tournament = models.ForeignKey(
        Tournament, null=False, blank=False, on_delete=models.PROTECT
    )
    matches = models.ManyToManyField(Match)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Match Submission Notes"
        unique_together = ("name", "tournament")


class Feature(models.Model):
    FEATURE_GROUP_REWARDS = 0

    f_choices = ((FEATURE_GROUP_REWARDS, "Group Rewards"),)

    feature_type = models.IntegerField(
        null=False, blank=False, choices=f_choices, default=FEATURE_GROUP_REWARDS
    )
    member_group = models.ForeignKey(
        MemberGroup,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="features",
    )
    enabled = models.BooleanField(null=False, default=False)
    tournament = models.ForeignKey(
        Tournament, blank=True, null=True, on_delete=models.PROTECT
    )
    tournament_format = models.IntegerField(
        null=False,
        blank=False,
        choices=TournamentFormats.type_choices(),
        default=TournamentFormats.T_TWENTY,
    )
    data_fn = PythonCodeField(
        default="lambda s: {'individual_contribution_amount': 0}",
        blank=False,
        null=False,
        max_length=200,
        validators=(is_code_and_lambda,),
    )

    def __str__(self):
        return "{} -- {}".format(self.feature_type, self.member_group)

    class Meta:
        unique_together = ("feature_type", "member_group")


reversion.register(ConfigItem)
reversion.register(MatchSubmissionNotes)
reversion.register(Feature)
