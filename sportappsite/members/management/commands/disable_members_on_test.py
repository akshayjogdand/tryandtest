from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from members.models import Member

from .random_passwords import m_p_mapping


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, **kwargs):
        for m in Member.objects.all():
            if m.id not in m_p_mapping:
                m.user.is_active = False
                m.user.save()
                m.save()

            else:
                rp = m_p_mapping.get(m.id)
                m.user.set_password(rp)
                m.user.save()
                m.save()
