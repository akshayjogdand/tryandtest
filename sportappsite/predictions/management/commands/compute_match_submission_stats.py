import logging
import time

from django.core.management.base import BaseCommand

from fixtures.models import Match

from stats.models import TeamStat, PlayerStat, PredictionFieldStat

from ...models import MemberSubmission

from ...stats import update_match_submission_stats, update_final_match_submission_stats

logger = logging.getLogger("p_a_computations")


class Command(BaseCommand):
    help = "Compute PA stats for a single Match."

    def add_arguments(self, parser):
        parser.add_argument("--match-id", required=False, type=int, help="Match ID")

        parser.add_argument(
            "--final-count",
            default=False,
            required=False,
            type=bool,
            help="Run Final Count OP",
        )

    def handle(self, match_id, final_count, **options):
        match = Match.objects.get(id=match_id)

        select = {
            "submission_type": MemberSubmission.MATCH_DATA_SUBMISSION,
            "is_valid": True,
            "member_group__reserved": False,
            "match": match,
        }

        logger.info(f"Computing/Re-computing Match PA stats for:\n\t\n{match}")
        logger.info("All Member Submissions will be processed.")
        logger.info("All previous stat records will be deleted.")

        time.sleep(5)

        logger.info(f"Locking Submisions for: {match}")
        old_ms_allowed = match.submissions_allowed
        old_pt_allowed = match.post_toss_changes_allowed
        match.submissions_allowed = False
        match.post_toss_changes_allowed = False
        match.save()

        ts = TeamStat.objects.filter(match=match)
        pfs = PredictionFieldStat.objects.filter(match=match)
        ps = PlayerStat.objects.filter(match=match, stat_name__startswith="selection_")

        for t in (ts, pfs, ps):
            logger.info(f"Removing {t.count()} records for {t.model}")
            t.delete()

        for ms in (
            MemberSubmission.objects.filter(**select).order_by("submission_time").all()
        ):
            update_match_submission_stats(ms.id)
            ms.p_a_computed = True
            ms.save()

        # Only do this if we want 0% stats for every combination of
        # (team stat,team + player stat,player + every range_stat) * member
        # groups + one more round for global.
        if final_count:
            update_final_match_submission_stats(match)

        logger.info(f"Un-Locking Submisions for: {match}")
        match.submissions_allowed = old_ms_allowed
        match.post_toss_changes_allowed = old_pt_allowed
        match.save()
