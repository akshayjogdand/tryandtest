from fixtures.models import Tournament

from sportappsite.constants import TournamentFormats

from django.core.management.base import BaseCommand

from django.db import transaction

from members.models import MemberGroup

from ...models import TournamentReward, TournamentRewardParticipant

AGREEMENT_TEXT = """
The following "Terms and Conditions" are an agreement between a "Member" on the FanAboard sports platform and the "Company" (FanAboard Technologies Pty Ltd).

These terms govern the Tournament Rewards.

There is no real money involved in any of the transactions for the entire Tournament on the platform; either from any Member to the Company, any Member to another Member, or Company to any Member.

Any money/credit/transaction shown is for illustration or demonstration purposes only.

All transactions and monetary amounts are in Australian dollars (AUD).

The Rewards shown on the individual account is a calculation based on the Member's actual participation and performance on the gaming platform.

The Rewards may keep changing based on the Member's participation and performance in each Match of the respective Tournament. This can happen before the start of the Match, during the Match, and/or after the Match finishes.

Administrator of the Member Group is allowed to add or remove Members to a Reward Pool.

Administrator of the Member Group is allowed to adjust the contribution amounts for each Member.

Under no circumstances should this concept should be copied or reproduced in any form.

The Group Rewards concept is for entertainment purposes only.

The Company reserves the rights to add more sub-features, modify the existing workflow, and/or remove the feature completely without informing the Members.

Copyright © 2019 | FanAboard Technologies Pty Ltd.
"""

REWARDS_CALCULATION_TEXT = """
Awards Distribution

Out of the total 100% of the Reward Pool collected/contributed, FanAboard Technologies Pty Ltd ("Company") will deduct 10% as their service charge.

The remaining 90% of the Reward Pool will be divided between all "Participating" Members. The Members can be nominated to participate by the Group administrator. The administrator decides the contribution amount for each Member resulting in the Total Reward Pool amount.

The distribution mechanism will be:

30% of the amount will be awarded to the Leaderboard Topper (1st position) at the end of the Tournament.

30% of the amount will be divided between the top 50% of the remaining Participants.

20% of the amount will be divided between the remaining Participants.

10% of the amount will be divided between the Participants' performances; applicable to any Participant.

FanAboard reserves the right to change this distribution mechanism.

"""


class Command(BaseCommand):
    help = "Create Initial Tournament Reward config for a given Tournament and Member Group"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tournament-id", required=True, type=int, help="Tournament ID"
        )

        parser.add_argument("--group-id", required=True, type=int, help="Group ID")

        parser.add_argument(
            "--tournament-format",
            required=True,
            type=int,
            help="Tournament Formats: {}".format(TournamentFormats.type_choices_str()),
        )

        parser.add_argument(
            "--individual-contribution-amount",
            required=True,
            type=int,
            help="How much should each Member contribute initially.",
        )

    @transaction.atomic
    def handle(
        self,
        tournament_id,
        group_id,
        tournament_format,
        individual_contribution_amount,
        **kwargs
    ):
        t = Tournament.objects.get(id=tournament_id)
        mg = MemberGroup.objects.get(id=group_id)
        tf = tournament_format  # TODO resolve this
        member_count = mg.members.count()

        try:
            tr = TournamentReward.objects.get(
                tournament=t, member_group=mg, tournament_format=tf
            )
        except TournamentReward.DoesNotExist:
            tr = TournamentReward()

        tr.tournament = t
        tr.member_group = mg
        tr.tournament_format = tf
        tr.contribution_per_member = individual_contribution_amount
        tr.suggested_reward_pool = member_count * individual_contribution_amount
        tr.reward_pool = member_count * individual_contribution_amount
        tr.changes_allowed_up_to = t.start_date
        tr.agreement_text = AGREEMENT_TEXT
        tr.rewards_calculations_text = REWARDS_CALCULATION_TEXT
        tr.save()

        for m in mg.members.all():
            try:
                trp = TournamentRewardParticipant.objects.get(reward=tr, member=m)
            except TournamentRewardParticipant.DoesNotExist:
                trp = TournamentRewardParticipant()
                trp.reward = tr
                trp.member = m
                trp.contributor = True
                trp.contribution_received = False

            trp.contribution_amount = individual_contribution_amount
            trp.save()
