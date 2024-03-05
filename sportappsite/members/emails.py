import datetime

from django_q.models import Schedule

from django.conf import settings

INVITE_TEXT = """
Hi {invitee},

{inviter} has invited you to participate in Member Group:
 {member_group} at FanAboard.

FanAboard is a free, fun and exciting way to test, share and refine
your cricket knowledge with family and friends.

Join or create a Member Group and start making Predictions around Tournaments,
Matches, Teams and Players. As each Match progresses, the system scores your
choices and awards points on a Group Leaderboard.

To join {inviter}'s group, register at:

    https://www.fanaboard.com/register and use the invite code: {code}

Remember, FanAboard is about cricket knowledge and skill, not luck....

Hope to see you there!

FanAboard team.

Please note: we do not support or endorse any form of gambling in FanAboard.
"""

PASSWORD_EMAIL_TEXT = """
Hi {member},

The password for your FanAboard account '{username}' has been reset:

Your new password is: '{new_password}'.

You can always change this after logging in:

  Click on your username (top left) and choose 'Change Password'.

Thank you!

FanAboard team.
"""

PASSWORD_RESET_SUBJECT = "Your FanAboard Password"

INVITE_SUBJECT = "Invitation to join {inviter} @FanAboard"

FROM_EMAIL = "noreply@fanaboard.com"

CONTACT_SUBJECT = "Contact query."

CONTACT_EMAIL_TEXT = """
From: {name}

Email: {email}

Mobile: {mobile_number}

=======================
{message}

"""

CONTACT_EMAIL = "info@fanaboard.com"

EMAIL_CONFIRM_EMAIL_TEXT = """
Hi {member},

Thank you for joining FanAboard

Before we get started, we will need to verify your mail.

Please click on the link below or paste it into your browser:
{verify_link}


Thank you!

FanAboard team.
"""

EMAIL_CONFIRM_SUBJECT = "Welcome to FanAboard!"

MEMBER_VERIFY_LINK = "https://{site}/member-verify/{type}/{token}"


def schedule_email(subject, text, from_addr, to_list, schedule_name, hook):
    Schedule.objects.create(
        func="django.core.mail.send_mail",
        hook=hook,
        args=(subject, text, from_addr, to_list),
        name=schedule_name,
        schedule_type=Schedule.ONCE,
    )


def send_invite_email(member_group_invitation):
    subject = INVITE_SUBJECT.format(inviter=member_group_invitation.inviter.name())

    text = INVITE_TEXT.format(
        inviter=member_group_invitation.inviter.name(),
        invitee=member_group_invitation.invited_name,
        code=member_group_invitation.invitation_code,
        member_group=member_group_invitation.member_group.name(),
    )

    schedule_email(
        subject,
        text,
        FROM_EMAIL,
        (member_group_invitation.invited_email,),
        schedule_name="Invite email {}".format(str(member_group_invitation)),
        hook="members.emails.invite_sent",
    )

    member_group_invitation.notification_sent = True
    member_group_invitation.notification_time = datetime.datetime.now(
        datetime.timezone.utc
    )
    member_group_invitation.save()


def send_password_reset_email(user, new_password):
    text = PASSWORD_EMAIL_TEXT.format(
        member=user.first_name, username=user.username, new_password=new_password
    )
    schedule_email(
        PASSWORD_RESET_SUBJECT,
        text,
        FROM_EMAIL,
        (user.email,),
        schedule_name="Password reset email for {}".format(user.username),
        hook="members.emails.password_reset_email_sent",
    )


def send_contact_email(name, email, mobile_number, message):
    text = CONTACT_EMAIL_TEXT.format(
        name=name, email=email, mobile_number=mobile_number, message=message
    )
    schedule_email(
        CONTACT_SUBJECT,
        text,
        FROM_EMAIL,
        (CONTACT_EMAIL,),
        schedule_name="Contact query email for {}".format(email),
        hook="members.emails.contact_us_email_sent",
    )


def send_member_email_verification_email(member_verification, resend=False):
    vl = MEMBER_VERIFY_LINK.format(
        site=settings.ALLOWED_HOSTS[0],
        token=member_verification.email_verification_token,
        type="email",
    )
    subject = EMAIL_CONFIRM_SUBJECT

    text = EMAIL_CONFIRM_EMAIL_TEXT.format(
        member=member_verification.member.name(), verify_link=vl
    )

    schedule_email(
        subject,
        text,
        FROM_EMAIL,
        (member_verification.email,),
        schedule_name="Email Verify {}".format(str(member_verification)),
        hook="members.emails.verify_email_sent",
    )

    if resend is False:
        member_verification.verification_email_sent = True
        member_verification.email_confirmation_ts = datetime.datetime.now(
            datetime.timezone.utc
        )
        member_verification.save()


def invite_sent(task):
    pass


def password_reset_email_sent(task):
    pass


def contact_us_email_sent(task):
    pass


def verify_email_sent(task):
    pass
