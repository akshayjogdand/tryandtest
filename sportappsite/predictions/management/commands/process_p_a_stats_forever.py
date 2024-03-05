import time
import logging

from django.core.management.base import BaseCommand

from django.utils import timezone

from ...models import MemberSubmission

from ...stats import update_match_submission_stats

logger = logging.getLogger("p_a_computations")

lstr = "Match PA stats processor"


def process_stats(batch_date):
    select = {
        "submission_type": MemberSubmission.MATCH_DATA_SUBMISSION,
        "is_valid": True,
        "member_group__reserved": False,
        "p_a_computed": False,
    }

    logger.info(f"{lstr}: Processing for batch: {batch_date}")

    unprocessed = MemberSubmission.objects.filter(**select).order_by("submission_time")
    t0 = timezone.now()
    logger.info(f"{lstr}: count={unprocessed.count()}")

    for ms in unprocessed:
        try:
            logger.info(f"{lstr}: START MS.id={ms.id}")
            update_match_submission_stats(ms.id)
            ms.p_a_computed = True
            ms.save()
            logger.info(f"{lstr}: FINISH MS.id={ms.id}")

        except Exception as ex:
            logger.exception(ex)
            logger.error(f"{lstr}: Error processing PA for MS.id={ms.id}")
            continue

    t1 = timezone.now()
    logger.info(
        f"{lstr}: Total processing time: {t1 - t0} for {unprocessed.count()} records"
    )


class Command(BaseCommand):
    help = "Process PA stats for Member Submissions in a loop."

    def handle(self, **options):
        batch = timezone.now()
        logger.info(f"{lstr}: starting at: {batch}")

        while True:
            batch = timezone.now()
            if batch.second % 10 == 0:
                process_stats(batch)
                time.sleep(5)
            else:
                time.sleep(1)
