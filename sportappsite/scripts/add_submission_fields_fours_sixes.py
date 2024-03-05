from django.db import transaction

from fixtures.models import Tournament

from predictions.models import GroupSubmissionsConfig, SubmissionFieldConfig


def new(g):
    predictions_submissionfieldconfig_272 = SubmissionFieldConfig()
    predictions_submissionfieldconfig_272.form_order = 9
    predictions_submissionfieldconfig_272.field = 31
    predictions_submissionfieldconfig_272.description = "Total Fours"
    predictions_submissionfieldconfig_272.is_compulsory = True
    predictions_submissionfieldconfig_272.is_enabled = True
    predictions_submissionfieldconfig_272.enable_for_matches = (
        "lambda match: match.match_number >= 48"
    )
    predictions_submissionfieldconfig_272.field_model = 3
    predictions_submissionfieldconfig_272.form_category = None
    predictions_submissionfieldconfig_272.group_submissions_config = g
    predictions_submissionfieldconfig_272.save()

    predictions_submissionfieldconfig_271 = SubmissionFieldConfig()
    predictions_submissionfieldconfig_271.form_order = 8
    predictions_submissionfieldconfig_271.field = 30
    predictions_submissionfieldconfig_271.description = "Total Sixes"
    predictions_submissionfieldconfig_271.is_compulsory = True
    predictions_submissionfieldconfig_271.is_enabled = True
    predictions_submissionfieldconfig_271.enable_for_matches = (
        "lambda match: match.match_number >= 48"
    )
    predictions_submissionfieldconfig_271.field_model = 3
    predictions_submissionfieldconfig_271.form_category = None
    predictions_submissionfieldconfig_271.group_submissions_config = g
    predictions_submissionfieldconfig_271.save()


@transaction.atomic
def run(*args):

    t = Tournament.objects.get(id=4)
    gcfs = GroupSubmissionsConfig.objects.filter(
        tournament=t, submission_type=GroupSubmissionsConfig.MATCH_DATA_SUBMISSION
    )

    for g in gcfs:
        new(g)
