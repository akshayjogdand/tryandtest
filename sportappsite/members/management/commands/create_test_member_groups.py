from django.core.management.base import BaseCommand

from django.db import transaction

from members.models import Membership, create_member, create_member_group_from_spare

from fixtures.models import Tournament


class Command(BaseCommand):
    help = "Create Indian and AU PMs Member Groups."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        t = Tournament.objects.get(id=37)

        mg = create_member_group_from_spare(None, "Indian PMs")
        mg.tournaments.add(t)
        mg.save()

        m1 = create_member(
            "jnehru@pmo.in", "Jawaharlal", "Nehru", "Wholetthedogsout!11", None
        )
        m2 = create_member(
            "rsashtri@pmo.in", "Ravi", "Sashtri", "Wholetthedogsout!11", None
        )
        m3 = create_member(
            "mdesai@pmo.in", "Morari", "Desai", "Wholetthedogsout!11", None
        )
        m4 = create_member(
            "igandhi@pmo.in", "Indira", "Gandhi", "Wholetthedogsout!11", None
        )
        m5 = create_member(
            "rgandhi@pmo.in", "Rajiv", "Gandhi", "Wholetthedogsout!11", None
        )

        for m in [m1, m2, m3, m4, m5]:
            m.email_verified = True
            ms = Membership()
            ms.member_group = mg
            ms.member = m
            ms.save()
            m.save()
            print(m.user.email)

        mg = create_member_group_from_spare(None, "Australian PMs")
        mg.tournaments.add(t)
        mg.save()

        m6 = create_member(
            "bhawke@pmo.com.au", "Bob", "Hawke", "Wholetthedogsout!11", None
        )
        m7 = create_member(
            "pkeating@pmo.com.au", "Paul", "Keating", "Wholetthedogsout!11", None
        )
        m8 = create_member(
            "krudd@pmo.com.au", "Kevin", "Rudd", "Wholetthedogsout!11", None
        )
        m9 = create_member(
            "jgillard@pmo.com.au", "Julia", "Gillard", "Wholetthedogsout!11", None
        )
        m10 = create_member(
            "mturnbull@pmo.com.au", "Malcolm", "Turnbull", "Wholetthedogsout!11", None
        )

        for m in [m6, m7, m8, m9, m10, m1]:
            m.email_verified = True
            ms = Membership()
            ms.member_group = mg
            ms.member = m
            ms.save()
            m.save()
            print(m.user.email)
