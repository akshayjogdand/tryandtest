import operator
import random
import secrets

from django.db import models
from django.db import transaction
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError


from reversion import revisions as reversion

from rules.models import (
    GroupPlayerScoringMethod,
    GroupPredictionScoringMethod,
    GroupPredictionSubmissionValidationRule,
    GroupPostMatchPredictionScoringMethod,
    GroupLeaderBoardScoringMethod,
    GroupTournamentScoringMethod,
)

from fixtures.models import Tournament, Match, Country


def generate_invite_code():
    from .utils import generate_invite_code as f

    return f()


def spare_member_group():
    return random.choice(MemberGroup.objects.filter(reserved=True))


@transaction.atomic
def create_member_group_from_spare(admin_member, group_name):

    group_name = group_name.title()

    try:
        Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        mg = spare_member_group()
        mg.reserved = False
        mg.group.name = group_name
        mg.group.save()
        mg.save()

        # Replace the spare group we just stole
        create_reserved_member_group()

        if admin_member:
            m = Membership()
            m.member = admin_member
            m.member_group = mg
            m.is_admin = True
            m.save()
    else:
        raise MemberGroupExists("Member Group with this name already exists.")

    return mg


@transaction.atomic
def create_reserved_member_group():
    group_name = secrets.token_hex(nbytes=16)
    try:
        Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        g = Group()
        g.name = group_name
        g.save()

        mg = MemberGroup()
        mg.group = g
        mg.reserved = True
        mg.save()

    else:
        raise MemberGroupExists("Member Group with this name already exists.")

    return mg


def member_exists(email):
    member = Member.objects.filter(user__username=email.lower()).first()
    if member:
        return member
    return None


@transaction.atomic
def create_member(email, first_name, last_name, password, invitation_code):
    member = Member()
    user = User()
    user.first_name = first_name.title()
    user.last_name = last_name.title()
    user.username = email.lower()
    user.email = email.lower()
    user.set_password(password)
    user.save()
    member.user = user
    member.save()

    invites = MemberGroupInvitation.objects.filter(invited_email=user.email)
    if invitation_code:
        invites = invites.exclude(invitation_code=invitation_code)

    for invite in invites:
        accept_invite(member, invite)

    if invitation_code:
        invitation_group = MemberGroup.objects.get(invitation_code=invitation_code)
        try:
            m = Membership.objects.get(member=member, member_group=invitation_group)
        except Membership.DoesNotExist:
            m = Membership(member=member, member_group=invitation_group)
            m.save()

    if len(invites) == 0 and invitation_code is None:
        add_to_default_member_group(member)

    return member


def accept_invite(member, invite):
    m = Membership()
    m.member = member
    m.member_group = invite.member_group
    invite.accepted = True
    invite.accepting_member = member
    invite.save()
    m.save()


def check_additional_invites(email, member, accepted_invite):
    invites = MemberGroupInvitation.objects.filter(invited_email=email)

    for invite in invites:
        if invite != accepted_invite:
            accept_invite(member, invite)


def add_to_default_member_group(member):
    from configurations.utils import get_default_member_group

    mg = get_default_member_group()
    try:
        m = Membership.objects.get(member=member, member_group=mg)
    except Membership.DoesNotExist:
        m = Membership()
        m.member = member
        m.member_group = mg

    m.active = True
    m.marked_inactive = None
    m.save()


def mobile_validator(value):
    if not (value and value.startswith("+")):
        raise ValidationError("mobile number should start with +")


class Member(models.Model):
    MALE = 1
    FEMALE = 2
    OTHER = 3
    NOTPREFER = 4
    gender_choices = (
        (MALE, "Male"),
        (FEMALE, "Female"),
        (OTHER, "Others"),
        (NOTPREFER, "Prefer Not To Say"),
    )
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    joined = models.DateTimeField(
        blank=True, null=False, editable=False, auto_now_add=True
    )
    email_verified = models.BooleanField(null=False, default=False)
    mobile_verified = models.BooleanField(null=False, default=False)
    nick_name = models.CharField(max_length=50, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.IntegerField(choices=gender_choices, blank=True, null=True)

    class Meta:
        ordering = ("user__first_name",)

    def name(self):
        return self.user.get_full_name()

    def __str__(self):
        return self.user.get_full_name()

    @staticmethod
    def autocomplete_search_fields():
        return ("user__first_name__icontains", "user__last_name__icontains")


# since user can change email so can't keep one to one mapping
class MemberVerification(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(
        max_length=20, null=True, blank=True, validators=[mobile_validator]
    )
    email_verification_token = models.CharField(
        max_length=255, null=True, blank=True, unique=True
    )
    mobile_verification_token = models.CharField(
        max_length=255, null=True, blank=True, unique=True
    )
    is_email_verified = models.BooleanField(null=False, default=False)
    is_mobile_verified = models.BooleanField(null=False, default=False)
    email_confirmation_ts = models.DateTimeField(null=True, blank=False)
    mobile_confirmation_ts = models.DateTimeField(null=True, blank=False)
    verification_email_sent = models.BooleanField(null=False, default=False)
    verification_sms_sent = models.BooleanField(null=False, default=False)
    created_on = models.DateTimeField(null=True, blank=False, auto_now_add=True)

    def __str__(self):
        return "{},{}".format(self.email, self.mobile)


class MemberGroup(models.Model):
    group = models.OneToOneField(Group, on_delete=models.PROTECT)
    created = models.DateTimeField(
        blank=True, null=False, editable=False, auto_now_add=True
    )
    members = models.ManyToManyField(Member, through="Membership")
    tournaments = models.ManyToManyField(
        Tournament, related_name="participating_member_groups"
    )
    invitation_code = models.CharField(
        max_length=10, blank=False, null=False, default=generate_invite_code
    )
    reserved = models.BooleanField(default=False)

    def name(self):
        return self.group.name

    def __str__(self):
        return self.name()

    @staticmethod
    def autcomplete_search_fields():
        return "group.name__icontains"


class MemberGroupExists(Exception):
    pass


class Membership(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    member_group = models.ForeignKey(MemberGroup, on_delete=models.CASCADE)
    notes = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    marked_inactive = models.DateTimeField(default=None, null=True, blank=True)
    is_admin = models.BooleanField(default=False, blank=False, null=False)
    active = models.BooleanField(default=True, blank=False, null=False)

    class Meta:
        unique_together = ("member", "member_group")
        ordering = ("member__user__first_name",)

    def __str__(self):
        return "Membership: {} in {}".format(
            self.member.name(), self.member_group.name()
        )


class MemberGroupInvitation(models.Model):
    inviter = models.ForeignKey(
        Member,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    accepting_member = models.ForeignKey(
        Member, null=True, blank=True, on_delete=models.CASCADE, related_name="+"
    )
    member_group = models.ForeignKey(
        MemberGroup, null=False, blank=False, on_delete=models.CASCADE
    )
    invited_name = models.CharField(max_length=50, null=False, blank=False)
    invited_email = models.EmailField(null=False, blank=False)
    invited_on = models.DateTimeField(null=False, auto_now_add=True, blank=False)
    notification_sent = models.BooleanField(null=False, default=False, blank=False)
    notification_time = models.DateTimeField(null=True, blank=True)
    accepted = models.BooleanField(null=False, default=False, blank=False)
    invitation_code = models.CharField(null=False, blank=False, max_length=10)

    def __str__(self):
        return "From: {} To: {} -- Member Group: {}".format(
            self.inviter.name(), self.invited_name, self.member_group.name()
        )


class MemberGroupRules(models.Model):
    member_group = models.ForeignKey(MemberGroup, on_delete=models.CASCADE)

    group_player_scoring_rules = models.ManyToManyField(
        GroupPlayerScoringMethod, blank=True
    )

    group_prediction_scoring_rules = models.ManyToManyField(
        GroupPredictionScoringMethod, blank=True
    )

    group_submission_validation_rules = models.ManyToManyField(
        GroupPredictionSubmissionValidationRule, blank=True
    )

    group_post_match_prediction_scoring_rules = models.ManyToManyField(
        GroupPostMatchPredictionScoringMethod, blank=True
    )

    group_leaderboard_scoring_rules = models.ManyToManyField(
        GroupLeaderBoardScoringMethod, blank=True
    )

    group_tournament_scoring_rules = models.ManyToManyField(
        GroupTournamentScoringMethod, blank=True
    )

    notes = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return "Group Rules for group: {}".format(self.member_group.group.name)

    class Meta:
        verbose_name_plural = "Member group rules"

    def rules(self):
        return (
            list(self.group_player_scoring_rules.all())
            + list(self.group_prediction_scoring_rules.all())
            + list(self.group_submission_validation_rules.all())
            + list(self.group_post_match_prediction_scoring_rules.all())
            + list(self.group_leaderboard_scoring_rules.all())
            + list(self.group_tournament_scoring_rules.all())
        )

    def parent_rules(self):
        return [r.parent_rule for r in self.rules()]


class GroupLeaderBoard(models.Model):
    member_group = models.ForeignKey(MemberGroup, on_delete=models.PROTECT)
    match = models.ForeignKey(Match, null=False, blank=False, on_delete=models.PROTECT)
    computed_on = models.DateTimeField(null=False, auto_now_add=True)
    board_number = models.IntegerField(null=False, default=0, blank=False)
    is_tournament_leaderboard = models.BooleanField(
        null=False, default=False, blank=False
    )

    def __str__(self):
        return "{} {}".format(self.member_group, self.match)

    def entries_relatively_positioned(self, member, field_name, position_fn):
        positioned = dict()
        try:
            member_entry = self.entries.get(member=member)
        except LeaderBoardEntry.DoesNotExist:
            return positioned

        all_entries_ordered = list(self.entries.order_by(field_name))

        entries = [
            e
            for e in all_entries_ordered
            if e.member != member and position_fn(e, member_entry)
        ]

        positioned = {e.member: e for e in entries}

        return positioned

    def top_score(self):
        entries_with_score = [e for e in self.entries.all() if e.this_match != 0]
        if len(entries_with_score) == 0:
            return 0

        member_score_rank = sorted(
            entries_with_score, reverse=True, key=operator.attrgetter("this_match")
        )
        return member_score_rank[0].this_match

    def entries_above(self, member):
        return self.entries_relatively_positioned(
            member,
            "-total",
            lambda entry, member_entry: entry.total > member_entry.total,
        )

    def entries_below(self, member):
        return self.entries_relatively_positioned(
            member,
            "-total",
            lambda entry, member_entry: entry.total < member_entry.total,
        )

    def entry(self, member):
        return self.entries.get(member=member)

    def tournament(self):
        return self.match.tournament

    # This method provides ALL Leaderboard available for a Member Group --
    # regardless of what Tournament, Match, etc. The only effective filter is
    # the Tournament status: active or not. Method serves to generate a list of
    # Leaderboard of a similar kind for a given Leaderboard -- kind meaning same
    # Member Group and Tournament Status.
    def available_leaderboards(self, memberships):
        data = []
        tournaments = []
        unique_tournaments = {}
        memberships = memberships.filter(member_group=self.member_group)
        m = memberships[0]

        boards = GroupLeaderBoard.objects.filter(
            match__tournament__is_active=self.match.tournament.is_active,
            member_group=self.member_group,
        )

        if not m.active:
            boards = boards.filter(
                match__tournament__start_date__lt=m.marked_inactive,
                match__match_date__lt=m.marked_inactive,
            )

        boards = boards.order_by("-match__tournament__start_date", "-match__match_date")

        for b in boards.all():
            unique_tournaments[b.match.tournament.id] = {
                "id": b.match.tournament.id,
                "name": b.match.tournament.name,
                "abbreviation": b.match.tournament.abbreviation,
            }
            data.append(
                {
                    "id": b.id,
                    "board_number": b.board_number,
                    "match": b.match.short_display_name,
                    "tournament_id": b.match.tournament.id,
                }
            )

        tournaments = []
        for t in unique_tournaments.items():
            tournaments.append(t[1])

        return {"data": data, "available_tournaments": tournaments}

    def format(self):
        return self.match.match_type

    class Meta:
        ordering = ["board_number"]


class LeaderBoardEntry(models.Model):
    member = models.ForeignKey(
        Member, null=False, blank=False, on_delete=models.PROTECT
    )
    leader_board = models.ForeignKey(
        GroupLeaderBoard,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    previous_points = models.FloatField(null=True, blank=True, default=0.0)
    this_match = models.FloatField(null=False, blank=False, default=0.0)
    tournament_predictions_score = models.FloatField(null=True, blank=True)
    total = models.FloatField(null=False, blank=False, default=0.00)
    previous_position = models.IntegerField(null=False, blank=False, default=0)
    position_now = models.IntegerField(null=False, blank=False, default=0)
    movement = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return "{}, []".format(self.member, self.total)

    def rank_movement(self):
        return "{0:+}".format(self.movement)

    class Meta:
        ordering = ["-total"]
        verbose_name_plural = "Leader Board Entries"


reversion.register(Member)
reversion.register(MemberGroup)
reversion.register(MemberGroupRules)
reversion.register(GroupLeaderBoard)
reversion.register(LeaderBoardEntry)
