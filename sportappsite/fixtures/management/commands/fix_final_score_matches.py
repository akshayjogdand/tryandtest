import logging

from django.core.management.base import BaseCommand

from fixtures.models import Match

from django.db import transaction


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **kwargs):
        for m in Match.objects.filter(fake_match=True):
            if m.tournament.bi_lateral == True:
                print(m)
                print(m.short_display_name)
                print(m.name)
                print('""""')
                m.assign_final_scores_match_name()
                print(m.short_display_name)
                print(m.name)
                print("====")
                m.save()
