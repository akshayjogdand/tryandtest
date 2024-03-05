from django.db import models

from members.models import Member, MemberGroup

from fixtures.models import Tournament


class MessageBlock(models.Model):
    message_name = models.CharField(
        unique=True, max_length=100, blank=False, null=False
    )
    content_block = models.TextField(max_length=None, blank=False, null=False)
    tournament = models.ForeignKey(
        Tournament, default=None, blank=True, null=True, on_delete=models.CASCADE
    )
    member = models.ForeignKey(
        Member, default=None, blank=True, null=True, on_delete=models.CASCADE
    )
    member_group = models.ForeignKey(
        MemberGroup, default=None, blank=True, null=True, on_delete=models.CASCADE
    )
    notes = models.TextField(max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.message_name
