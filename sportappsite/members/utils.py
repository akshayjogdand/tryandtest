import uuid
import random
import logging
import datetime

from rules.models import RULE_TO_MEMBER_GROUP_RULE_MAPPING

from rules.utils import clone_rule, update_cloned_rule

from fixtures.models import Tournament

from configurations.utils import get_default_tournament_rules

from predictions.utils import create_or_update_submission_config_for_tournament

from .models import (
    Member,
    Membership,
    MemberGroupRules,
    MemberGroup,
    MemberVerification,
)

from .emails import send_password_reset_email, send_member_email_verification_email

logger = logging.getLogger("django")


def mg_and_add_currently_active_tournaments(member_group_id):
    mg = MemberGroup.objects.get(id=member_group_id)
    add_currently_active_tournaments(mg)


def add_currently_active_tournaments(member_group):
    for t in Tournament.objects.filter(is_active=True):
        member_group.tournaments.add(t)

    member_group.save()


def create_new_group_rules(member_group_rules, tournament):

    for default_rule in get_default_tournament_rules(tournament):
        gr_klass, klass_var = RULE_TO_MEMBER_GROUP_RULE_MAPPING.get(type(default_rule))

        group_rule = clone_rule(default_rule, gr_klass)
        group_rule.is_default = False
        group_rule.save()

        getattr(member_group_rules, klass_var).add(group_rule)

    member_group_rules.save()


def update_existing_group_rules(member_group_rules, tournament):
    default_rules = set(get_default_tournament_rules(tournament))
    group_parent_rules = set(member_group_rules.parent_rules())

    missing = default_rules.difference(group_parent_rules)
    to_update = default_rules.intersection(group_parent_rules)

    for mr in missing:
        gr_klass, klass_var = RULE_TO_MEMBER_GROUP_RULE_MAPPING.get(type(mr))

        group_rule = clone_rule(mr, gr_klass)
        group_rule.is_default = False
        group_rule.save()

        getattr(member_group_rules, klass_var).add(group_rule)

    # For now assume this step is not needed -- i.e. the orignal group rules
    # are correctly created and updates have been passed on via clone mechanism.
    #
    # TODO if gr was in missing above, it already has latest copy, no need to update.
    # for gr in member_group_rules.rules():
    # for pr in default_rules:
    # if gr.parent_rule == pr:
    # update_cloned_rule(pr, gr)
    # gr.save()

    # TODO
    # remove rules not present in default_rules


def get_or_create_group_rules_from_defaults(member_group, tournament):
    try:
        member_group_rules = MemberGroupRules.objects.get(member_group=member_group)
    except MemberGroupRules.DoesNotExist:
        member_group_rules = MemberGroupRules()
        member_group_rules.member_group = member_group
        member_group_rules.save()
        create_new_group_rules(member_group_rules, tournament)
    else:
        update_existing_group_rules(member_group_rules, tournament)


def generate_invite_code(length=8):
    return "".join(map(lambda _: random.choice(uuid.uuid4().hex), range(length)))


def generate_password():
    return "".join(
        map(lambda _: random.choice(uuid.uuid4().hex), range(random.randrange(15, 30)))
    )


def reset_member_password(user_email):
    try:
        member = Member.objects.get(user__email=user_email)
    except Member.DoesNotExist:
        logger.warning(
            "Attempt to reset password for: {}; " "Member not found".format(user_email)
        )
        return

    new_password = generate_password()
    member.user.set_password(new_password)
    member.user.save()

    send_password_reset_email(member.user, new_password)


def resolve_member(user):
    return Member.objects.get(user=user)


# if all as true then it will return all members including inactive
def member_memberships(user, inactive=False):
    try:
        member = Member.objects.get(user=user)
        memberships = Membership.objects.filter(member=member)

        if not inactive:
            memberships = memberships.filter(active=True)

        memberships = memberships.order_by("member_group__group__name")

    # TODO raise proper exceptions
    except Member.DoesNotExist:
        raise
    except Membership.DoesNotExist:
        raise

    return member, memberships


def has_active_membership(memberships, member_group):
    for m in memberships:
        if m.member_group == member_group:
            return m.active

    return False


def has_membership(memberships, member_group):
    if isinstance(member_group, int):
        return member_group in [m.member_group_id for m in memberships]
    else:
        return member_group in [m.member_group for m in memberships]


def generate_member_token(member, length=14):
    return (
        str(hash(member.user.email))
        + "".join(map(lambda _: random.choice(uuid.uuid4().hex), range(length)))
    ).replace("-", "")


def verify_member_email(member, resend=False):
    if not (member.email_verified):
        mv = MemberVerification()

        # get latest first record from db
        mvs = MemberVerification.objects.filter(member=member).order_by("-created_on")
        if mvs.count() > 0:
            mv = mvs[0]
        else:
            mv.member = member
            mv.email = member.user.email
            mv.email_verification_token = generate_member_token(member)

        # if record is available and email is already sent
        # then dont resend mail
        if not mv.verification_email_sent or resend is True:
            send_member_email_verification_email(mv, resend)

        mv.save()


def set_member_email_as_verfied(token):
    mvs = MemberVerification.objects.filter(email_verification_token=token)
    if mvs.count() == 1:
        mv = mvs[0]
        if mv.member.email_verified:
            return False

        mv.is_email_verified = True
        mv.email_confirmation_ts = datetime.datetime.now(datetime.timezone.utc)
        mv.member.email_verified = True
        mv.member.save()
        mv.save()
        return True

    return False
