from django.core.management.base import BaseCommand
from members.models import create_member, member_exists


class Command(BaseCommand):
    help = "Create member account for testing"

    def handle(self, *args, **kwargs):
        self.create_test_user()

    def create_test_user(self):
        print("create test app user: ")

        first_name = "Test"
        last_name = "User"
        username = "testuser@fanaboard.com"
        password = "testuserpass"

        if member_exists(username):
            print("{} is already exist".format(username))
        else:
            create_member(username, first_name, last_name, password, "")
            print("{} created".format(username))
