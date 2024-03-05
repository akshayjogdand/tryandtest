from django.db.models.signals import post_save

from django.dispatch import receiver

from imports.models import DataImport

from predictions.management.commands.import_member_predictions import Command


@receiver(post_save, sender=DataImport)
def import_file_saved(sender, instance, **kwargs):

    if instance.import_type != DataImport.IMPORT_MEMBER_PREDICTIONS:
        return

    c = Command()
    c.handle(instance.match.id, instance.member_group.id, instance.data_file.file.name)
