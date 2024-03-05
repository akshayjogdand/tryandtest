from django.db import models


class AccessAttempt(models.Model):
    ip_address = models.GenericIPAddressField(null=True, db_index=True)
    username = models.CharField(max_length=255, null=True, db_index=True)
    path = models.CharField(max_length=255, null=True)
    accessed_on = models.DateTimeField(null=False, auto_now_add=True)

    def __str__(self):
        return self.username + " @ " + self.attempt_time
