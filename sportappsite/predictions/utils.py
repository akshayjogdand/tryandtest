from sportappsite.constants import control_group

from .models import (
    GroupSubmissionsConfig,
    ControlledGroupSubmissionsConfig,
)


def create_or_update_submission_config_for_tournament(member_group, tournament):
    for c in ControlledGroupSubmissionsConfig.objects.filter(tournament=tournament):
        create_or_update_submission_config(member_group, c)


def create_or_update_submission_config(member_group, controlled_config):
    # No need to create a config for this Member Group.
    if member_group == control_group():
        return

    try:
        group_config = GroupSubmissionsConfig.objects.get(
            tournament=controlled_config.tournament,
            member_group=member_group,
            submission_type=controlled_config.submission_type,
            tournament_format=controlled_config.tournament_format,
        )
    except GroupSubmissionsConfig.DoesNotExist:
        group_config = GroupSubmissionsConfig()
        group_config.member_group = member_group
        group_config.tournament = controlled_config.tournament
        group_config.tournament_format = controlled_config.tournament_format
        group_config.submission_type = controlled_config.submission_type

    # ControlledGroupSubmissionsConfig is also a GroupSubmissionsConfig
    # If you allow this, all the SubmissionFieldConfig disappear.
    if group_config.id == controlled_config.id:
        return

    group_config.submission_notes = controlled_config.submission_notes
    group_config.display_table_ordering = controlled_config.display_table_ordering
    group_config.active_from = controlled_config.active_from
    group_config.active_to = controlled_config.active_to
    group_config.save()

    for f in group_config.submission_fields.all():
        f.delete()

    controlled_fields = controlled_config.submission_fields.all().order_by("form_order")
    for f in controlled_fields.all():
        f.pk = None
        f.id = None
        f.group_submissions_config = group_config
        f.save()

    return group_config


def clone_controlled_config(tournament, controlled_config):
    group_config = ControlledGroupSubmissionsConfig()
    group_config.member_group = control_group()
    group_config.tournament = tournament
    group_config.tournament_format = controlled_config.tournament_format
    group_config.submission_type = controlled_config.submission_type

    group_config.submission_notes = controlled_config.submission_notes
    group_config.display_table_ordering = controlled_config.display_table_ordering
    group_config.save()

    controlled_fields = controlled_config.submission_fields.all().order_by("form_order")
    for f in controlled_fields.all():
        f.pk = None
        f.id = None
        f.group_submissions_config = group_config
        f.save()

    return group_config
