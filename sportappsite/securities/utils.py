from django.utils import timezone
from .models import AccessAttempt
from captcha.models import CaptchaStore
from datetime import timedelta


def verify_captcha(hashkey, value):
    try:
        c = CaptchaStore.objects.get(hashkey=hashkey)
        if c.response == value.lower():
            c.delete()
            return True
    except Exception:
        pass
    return False


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# if 5 attempts done in 15 mins then don't allow user to login for next attempts
def count_access_attempts(ip, minutes=15):
    attempts_in = timezone.now() - timedelta(minutes=minutes)
    aa = AccessAttempt.objects.filter(ip_address=ip, accessed_on__gte=attempts_in)
    return aa.count()


def create_access_attempts(ip, path, username):
    aa = AccessAttempt()
    aa.ip_address = ip
    aa.path = path
    aa.username = username
    aa.save()


def clear_access_attempts(request):
    ip = get_client_ip(request)
    AccessAttempt.objects.filter(ip_address=ip).delete()


def is_access_allowed(request, username=""):
    if username == "":
        username = request.data["username"]
    ip = get_client_ip(request)
    path = request.get_full_path()
    if count_access_attempts(ip) < 5:
        create_access_attempts(ip, path, username)
        return True
    else:
        return False
