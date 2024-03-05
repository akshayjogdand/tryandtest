import arrow

from django.db import models

from reversion import revisions as reversion

from members.models import Member, MemberGroup

from fixtures.models import Tournament

from sportappsite.constants import TournamentFormats


class TournamentReward(models.Model):
    tournament = models.ForeignKey(
        Tournament, null=False, blank=False, on_delete=models.PROTECT
    )
    tournament_format = models.IntegerField(
        null=False,
        blank=False,
        choices=TournamentFormats.type_choices(),
        default=TournamentFormats.T_TWENTY.value,
    )
    member_group = models.ForeignKey(
        MemberGroup, null=False, blank=False, on_delete=models.PROTECT
    )
    suggested_reward_pool = models.IntegerField(null=False, blank=False, default=0)
    reward_pool = models.IntegerField(null=False, blank=False, default=0)
    contribution_per_member = models.IntegerField(null=False, blank=False, default=0)
    is_financial = models.BooleanField(null=False, default=True)
    activated = models.BooleanField(null=False, default=False)
    agreement_text = models.TextField(null=True, blank=True)
    rewards_calculations_text = models.TextField(null=True, blank=True)
    changes_allowed_up_to = models.DateTimeField(null=False, blank=False)

    class Meta:
        unique_together = ("tournament", "tournament_format", "member_group")

    def __str__(self):
        return "Reward config for {}, {}".format(self.member_group, self.tournament)

    def changes_allowed_up_to_utc(self):
        if self.changes_allowed_up_to:
            return arrow.get(self.changes_allowed_up_to).format(
                "dddd DD/MM/YYYY h:mm A"
            )


class TournamentRewardParticipant(models.Model):
    member = models.ForeignKey(
        Member, null=False, blank=False, on_delete=models.PROTECT
    )
    reward = models.ForeignKey(
        TournamentReward,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="participants",
    )
    contributor = models.BooleanField(default=True)
    contribution_amount = models.IntegerField(null=False, blank=False)
    contribution_received = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)


class TournamentRewardAgreement(models.Model):
    admin_member = models.ForeignKey(
        Member, null=False, blank=False, on_delete=models.PROTECT
    )
    reward = models.ForeignKey(
        TournamentReward,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="agreement_records",
    )
    date_agreed = models.DateTimeField(auto_now_add=True)
    agreement_text = models.TextField(null=False, blank=False, editable=False)
    rewards_calculations_text = models.TextField(null=True, blank=True)


reversion.register(TournamentReward)
reversion.register(TournamentRewardParticipant)
reversion.register(TournamentRewardAgreement)
