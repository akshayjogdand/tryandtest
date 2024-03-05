from members.models import Member, MemberGroup, Membership


def run(member_id, member_group_id):
    member = Member.objects.get(id=member_id)
    member_group = MemberGroup.objects.get(id=member_group_id)
    m = Membership()
    m.member_group = member_group
    m.member = member
    m.save()
    print("Added {} to group {}".format(member, member_group))
