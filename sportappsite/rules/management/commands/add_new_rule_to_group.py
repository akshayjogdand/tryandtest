from django.core.management.base import BaseCommand, CommandError

from django.db import transaction

from rules.models import (
    PlayerScoringMethod,
    PredictionScoringMethod,
    PredictionSubmissionValidationRule,
    PostMatchPredictionScoringMethod,
    LeaderBoardScoringMethod,
)

from members.models import MemberGroupRules, MemberGroup

from rules.utils import clone_rule

from rules.models import RULE_TO_MEMBER_GROUP_RULE_MAPPING


def get_rule_type(arg):
    mapping = {
        "1": PlayerScoringMethod,
        "2": PredictionScoringMethod,
        "3": PredictionSubmissionValidationRule,
        "4": PostMatchPredictionScoringMethod,
        "5": LeaderBoardScoringMethod,
    }

    return mapping[arg.strip()]


class Command(BaseCommand):
    help = "Take a given Rule, clone it and add it to a MemberGroup's rules"

    def add_arguments(self, parser):
        parser.add_argument(
            "--rule-type",
            required=True,
            type=get_rule_type,
            help=(
                "Rule Type to clone, choose number: "
                "1 = PlayerScoringMethod, "
                "2 = PredictionScoringMethod, "
                "3 = PredictionValidationRule, "
                "4 = PostMatchPredictionScoringMethod, "
                "5 = LeaderBoardScoringMethod"
            ),
        )

        parser.add_argument(
            "--rule-id", required=True, type=int, help="Rule ID to clone"
        )

        parser.add_argument(
            "--member-group-id",
            required=True,
            type=int,
            help="Member Group ID to which cloned rule will be applied",
        )

    @transaction.atomic
    def handle(self, rule_type, rule_id, member_group_id, *args, **kwargs):
        try:
            mg = MemberGroup.objects.get(id=member_group_id)
            mgr = MemberGroupRules.objects.get(member_group=mg)
            rule = rule_type.objects.get(id=rule_id)
            group_rule_type, var_name = RULE_TO_MEMBER_GROUP_RULE_MAPPING.get(rule_type)
            new_rule = clone_rule(rule, group_rule_type)
            new_rule.save()
            getattr(mgr, var_name).add(new_rule)
            mgr.save()
            self.stdout.write(
                "Added new {}, ID: {}, Name: {} to MemberGroup: {}".format(
                    group_rule_type, new_rule.id, new_rule.name, mg
                )
            )
        except MemberGroup.DoesNotExist:
            raise CommandError(
                "Member Group with ID: {} does not exist".format(member_group_id)
            )
        except MemberGroupRules.DoesNotExist:
            raise CommandError(
                "Member Group with ID: {} does not have any Rules".format(
                    member_group_id
                )
            )
        except rule_type.DoesNotExist:
            raise CommandError(
                "Rule of type: {} with ID: {} does not exist.".format(
                    rule_type, rule_id
                )
            )
        except Exception as ex:
            raise (ex)
