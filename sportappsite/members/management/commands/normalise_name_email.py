from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, **kwargs):
        users = User.objects.all()
        for user in users:
            user.first_name = user.first_name.title()
            user.last_name = user.last_name.title()
            user.email = user.email.lower()
            user.save()
        return print("All name and email of user collection are normalised")
