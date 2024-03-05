from members.models import MemberGroup, Membership


def run(*args):
    for g in MemberGroup.objects.all():
        print("====================\n" "{}\n" "====================".format(g))
        for ms in Membership.objects.filter(member_group=g).all():
            print(ms.member)
        print("\n")
