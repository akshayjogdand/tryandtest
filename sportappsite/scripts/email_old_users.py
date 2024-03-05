from members.models import Member
from members.emails import schedule_email, FROM_EMAIL
from members.utils import generate_password

from django_q.models import Success

SUBJECT = "Your FanAboard account."

TEXT = """
Hi {member},

Your FanAboard account is now active!

Please login at:

  https://www.fanaboard.com/

username: '{username}'
password: '{password}'

You can always change your password after logging in:

  Click on your username (top left) and choose 'Change Password'.

FanAboard is a free, fun and exciting way to test, share and refine
your cricket knowledge with family and friends.

Join or create a Member Group and start making Predictions around Tournaments,
Matches, Teams and Players. As each Match progresses, the system scores your
choices and awards points on a Group Leaderboard.

Remember, FanAboard is about cricket knowledge and skill, not luck....

Hope to see you there!

FanAboard team.

Please note: we do not support or endorse any form of gambling in FanAboard.
"""


def already_sent(member):
    s = Success.objects.filter(group__contains=member.name())
    return s.exists()


def run(*args):
    for member in Member.objects.all():
        if member.user.email and "test.com" not in member.user.email:
            if already_sent(member):
                print(member)
                continue

            password = generate_password()
            member.user.set_password(password)
            member.user.save()
            text = TEXT.format(
                member=member.user.first_name,
                username=member.user.username,
                password=password,
            )

            schedule_email(
                SUBJECT,
                text,
                FROM_EMAIL,
                (member.user.email,),
                schedule_name="Old members account activation email: {}".format(
                    str(member.name())
                ),
                hook="",
            )
