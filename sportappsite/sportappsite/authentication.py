from django.middleware import csrf
from rest_framework.authentication import CSRFCheck
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import exceptions


class JWTSessionAuthentication(JSONWebTokenAuthentication):
    """
      Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
  """

    def get_jwt_value(self, request):
        jwt_value = super().get_jwt_value(request)
        if jwt_value is None:
            return None

        # force for csrf validation
        self.enforce_csrf(request)
        return jwt_value

    def enforce_csrf(self, request):
        """
      Enforce CSRF validation for session based authentication.
      """
        csrf.get_token(request)
        reason = CSRFCheck().process_view(request, None, (), {})
        if reason:
            # CSRF failed, bail with explicit error message
            raise exceptions.PermissionDenied("CSRF Failed: %s" % reason)
