from rules.management.commands import add_new_rule_to_group
from members.models import MemberGroup

C = add_new_rule_to_group.Command()


def run():
    rt = add_new_rule_to_group.get_rule_type("4")

    for mg in MemberGroup.objects.all():
        C.handle(rt, 23, mg.id)
        C.handle(rt, 24, mg.id)
        C.handle(rt, 25, mg.id)
