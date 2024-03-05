from django_q.models import Schedule

from django.utils import timezone


def add_currently_active_tournaments_schedule(member_group):
    Schedule.objects.create(
        func="members.utils.mg_and_add_currently_active_tournaments",
        args=member_group.id,
        name="New Member Group: {}, add active Tournaments + Rules".format(
            member_group.name()
        ),
        schedule_type=Schedule.ONCE,
        next_run=timezone.now(),
    )
