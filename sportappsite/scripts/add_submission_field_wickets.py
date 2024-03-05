from django.db import transaction

from fixtures.models import Tournament

from predictions.models import GroupSubmissionsConfig, SubmissionFieldConfig


def new():
    predictions_submissionfieldconfig_257 = SubmissionFieldConfig()
    predictions_submissionfieldconfig_257.form_order = 7
    predictions_submissionfieldconfig_257.field = 22
    predictions_submissionfieldconfig_257.description = "Total Wickets"
    predictions_submissionfieldconfig_257.is_compulsory = True
    predictions_submissionfieldconfig_257.is_enabled = True
    predictions_submissionfieldconfig_257.enable_for_matches = (
        "lambda match: match.match_number >= 39"
    )
    predictions_submissionfieldconfig_257.field_model = 3
    predictions_submissionfieldconfig_257.form_category = None

    return predictions_submissionfieldconfig_257


@transaction.atomic
def run(*args):

    t = Tournament.objects.get(id=4)
    gcfs = GroupSubmissionsConfig.objects.filter(
        tournament=t, submission_type=GroupSubmissionsConfig.MATCH_DATA_SUBMISSION
    )

    for g in gcfs:
        f = new()
        f.group_submissions_config = g
        f.save()
