from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from rules.models import RULE_TO_MEMBER_GROUP_RULE_MAPPING

from rules.utils import clone_rule

from members.models import MemberGroupRules, MemberGroup

from sportappsite.constants import TournamentFormats


class Command(BaseCommand):
    help = "Ensure all old Member Groups have a copy of new format Rules"

    @transaction.atomic
    def handle(self, *args, **options):
        for mgr in MemberGroupRules.objects.all():
            for (
                parent_class,
                (group_class, var_name),
            ) in RULE_TO_MEMBER_GROUP_RULE_MAPPING.items():
                for r_format in (
                    TournamentFormats.ONE_DAY.value,
                    TournamentFormats.TEST.value,
                ):

                    group_rules_var = getattr(mgr, var_name)
                    parent_rules = set(
                        parent_class.objects.filter(apply_to_match_type=r_format).all()
                    )
                    group_rules = set([r.parent_rule for r in group_rules_var.all()])

                    missing = parent_rules.difference(group_rules)

                    for m in missing:
                        gr = clone_rule(m, group_class)
                        gr.is_default = False
                        gr.save()
                        group_rules_var.add(gr)

                mgr.save()
