from rest_framework_jwt.utils import jwt_payload_handler

from drf_api.views import member_memberships


def member_jwt_payload_handler(user):
    member, _ = member_memberships(user)
    payload = jwt_payload_handler(user)

    if member:
        payload["member_id"] = member.id
        payload["first_name"] = member.user.first_name
        payload["last_name"] = member.user.last_name

    return payload
