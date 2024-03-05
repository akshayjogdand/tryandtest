from django.core.mail import send_mail


def run(*args):
    send_mail(
        "FanAboard test email",
        "Here is the message.",
        "noreply@fanaboard.com",
        ["sawan.vithlani@fanaboard.com"],
        fail_silently=False,
    )
