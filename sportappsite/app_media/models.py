import uuid
import os
import random

from django.conf import settings
from django.db import models
from django.utils.deconstruct import deconstructible
from reversion import revisions as reversion

from python_field.python_field import PythonCodeField
from python_field.utils import is_code_and_lambda

from fixtures.models import Country, Player, Team, Tournament
from members.models import Member


def generate_file_name(length=10):
    return "".join(map(lambda _: random.choice(uuid.uuid4().hex), range(length)))


def set_path_and_file_name(instance, filename):
    path = settings.MEDIA_DIR["app_media"]
    instance.media_name = generate_file_name()
    instance.original_filename = filename
    ext = filename.split(".")[-1]
    new_filename = "{}.{}".format(instance.media_name, ext)
    if os.path.exists(instance.media_file.path):
        os.remove(instance.media_file.path)
    return os.path.join(path, new_filename)


# Below class is not being used
# kept it bcoz migration files was showing error
# can remove all migration file and remove this function and regenerate migration for this app
@deconstructible
class PathAndRename(object):
    def __call__(self, instance, filename):
        return ""


class AppMedia(models.Model):
    _SPEC_LAMBDA = "lambda : True"

    # media sizes
    ICON = 1
    SMALL = 2
    MEDIUM = 3
    LARGE = 4
    BANNER = 5

    # type
    IMAGE = 1
    VIDEO = 2

    media_size_choices = [
        (ICON, "icon"),
        (SMALL, "small"),
        (MEDIUM, "medium"),
        (LARGE, "large"),
        (BANNER, "banner"),
    ]

    media_type_choices = [(IMAGE, "image"), (VIDEO, "video")]

    media_name = models.CharField(
        default=generate_file_name, max_length=10, unique=True
    )
    media_size = models.IntegerField(choices=media_size_choices)
    media_type = models.IntegerField(choices=media_type_choices)
    media_file = models.FileField(upload_to=set_path_and_file_name)

    original_filename = models.CharField(
        max_length=200, default=None, blank=True, null=True
    )
    media_note = models.TextField(default=None, blank=True, null=True)
    media_spec = PythonCodeField(
        default=_SPEC_LAMBDA,
        blank=False,
        null=False,
        max_length=200,
        validators=(is_code_and_lambda,),
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
        related_name="media",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
        related_name="media",
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
        related_name="media",
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
        related_name="avatar",
    )
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
        related_name="media",
    )

    def __str__(self):
        return "{}".format(self.media_name)


reversion.register(AppMedia)
