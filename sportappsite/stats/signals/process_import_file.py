from django.db.models.signals import post_save

from django.dispatch import receiver

from imports.models import DataImport

from stats.management.commands.import_player_performances import Command


@receiver(post_save, sender=DataImport)
def import_file_saved(sender, instance, **kwargs):

    performance_import_map = {
        DataImport.IMPORT_BATTING_PERFORMANCE: "batting",
        DataImport.IMPORT_BOWLING_PERFORMANCE: "bowling",
        DataImport.IMPORT_FIELDING_PERFORMANCE: "fielding",
        DataImport.IMPORT_MATCH_PERFORMANCE: "match-stats",
        DataImport.IMPORT_MATCH_DATA: "match",
    }

    if instance.import_type not in performance_import_map.keys():
        return

    c = Command()
    c.handle(
        performance_import_map.get(instance.import_type),
        instance.data_file.file.name,
        instance.match.id,
    )
