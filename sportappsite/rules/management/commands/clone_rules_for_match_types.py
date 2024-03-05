from django.core.management.base import BaseCommand, CommandError

from django.db import transaction

from rules.models import Rule, DEFAULT_RULE_TYPES


class Command(BaseCommand):
    help = "Take a given Rule for default Match type and clone it for other Match Types"

    @transaction.atomic
    def handle(*args, **kwargs):
        for rule_type in DEFAULT_RULE_TYPES:
            for parent_rule in rule_type.objects.filter(
                apply_to_match_type=Rule.T_TWENTY
            ):

                parent_rule.id = None
                parent_rule.pk = None
                parent_rule.apply_to_match_type = Rule.ONE_DAY
                parent_rule.save()

                parent_rule.id = None
                parent_rule.pk = None
                parent_rule.apply_to_match_type = Rule.TEST
                parent_rule.save()
