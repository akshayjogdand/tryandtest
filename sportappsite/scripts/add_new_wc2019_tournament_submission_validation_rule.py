from rules.management.commands import add_new_rule_to_group
from members.models import MemberGroup

C = add_new_rule_to_group.Command()


def run():
    rt = add_new_rule_to_group.get_rule_type("3")

    for mg in MemberGroup.objects.all():
        C.handle(rt, 9, mg.id)
