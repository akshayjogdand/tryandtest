from django.contrib import admin

from reversion.admin import VersionAdmin

import easy

from csv_export.views import CSVExportView

from scoring.utils import rule_results_as_table

from members.models import MemberGroup

from .models import (
    MemberPrediction,
    PredictionSubmissionValidations,
    PredictionScores,
    PostPredictionScores,
    MemberSubmissionData,
    GroupSubmissionsConfig,
    SubmissionFieldConfig,
    MemberTournamentPrediction,
    MemberSubmission,
    TouramentPredictionScore,
    ControlledGroupSubmissionsConfig,
)

from .utils import create_or_update_submission_config


class PatchedCSVExportView(CSVExportView):
    def get_field_value(self, related_obj, related_field_name):
        if not related_obj:
            return ""

        return super(PatchedCSVExportView, self).get_field_value(
            related_obj, related_field_name
        )


class MemberPredictionAdmin(VersionAdmin):
    exclude = ()
    readonly_fields = [
        "winning_team",
        "winning_team_score",
        "winning_team_calculated_winning_score",
        "winning_team_final_winning_score",
        "player_one_score",
        "player_two_score",
        "player_three_score",
        "player_four_score",
        "player_five_score",
        "super_player_score",
        "total_prediction_score",
        "prediction_scores",
        "post_prediction_scores",
        "leaderboard_scores",
    ]
    search_fields = (
        "member_group__group__name",
        "member__user__first_name",
        "member__user__last_name",
        "match__name",
    )
    list_filter = [
        "member_group__group__name",
        "member__user__first_name",
        "member__user__last_name",
        "match__name",
        "match__match_type",
        "match__tournament__name",
    ]
    list_display = [
        "member",
        "member_group",
        "match",
        "predicted_winning_team",
        "predicted_winning_team_score",
        "total_prediction_score",
    ]

    actions = ("export_data_csv",)

    def export_data_csv(self, request, queryset):
        f = (
            "member__user__first_name",
            "member__user__last_name",
            "member_group__group__name",
            "match__name",
            "match__match_number",
            "player_one__name",
            "player_two__name",
            "player_three__name",
            "super_player__name",
            "predicted_winning_team__name",
            "predicted_winning_team_score",
            "total_wickets",
            "total_fours",
            "total_sixes",
            "total_prediction_score",
        )
        qs = queryset.order_by("match__match_number")
        view = PatchedCSVExportView(queryset=qs, fields=f)
        return view.get(request)

    export_data_csv.short_description = "Export CSV for selected records"


class PredictionSubmissionValidationsAdmin(VersionAdmin):
    pass


class PredictionScoresAdmin(VersionAdmin):
    readonly_fields = ("total_score", "results_as_table")
    list_display = ("__str__",)
    search_fields = ("id", "total_score")
    exclude = ("detailed_scoring",)
    search_fields = ("id", "total_score")

    @easy.with_tags()
    @easy.short(desc="Scoring")
    def results_as_table(self, instance):
        return rule_results_as_table(instance.detailed_scoring.all())


class PostPredictionScoresAdmin(VersionAdmin):
    readonly_fields = ("total_score", "results_as_table")
    list_display = ("__str__",)
    search_fields = ("id", "total_score")
    exclude = ("detailed_scoring",)

    @easy.with_tags()
    @easy.short(desc="Scoring")
    def results_as_table(self, instance):
        return rule_results_as_table(instance.detailed_scoring.all())


class SubmissionDataInline(admin.TabularInline):
    model = MemberSubmissionData
    can_delete = False
    show_change_link = False
    extra = 0
    readonly_fields = ("field_name", "player", "team", "value")
    ordering = ("field_name",)


class MemberSubmissionAdmin(VersionAdmin):
    inlines = [SubmissionDataInline]
    list_filter = (
        "member",
        "member_group",
        "match",
        "tournament",
        "submission_type",
        "submission_format",
    )
    search_fields = (
        "member_group__group__name",
        "member__user__first_name",
        "member__user__last_name",
        "match__name",
    )
    list_display = (
        "id",
        "match",
        "tournament",
        "member_group",
        "member",
        "is_valid",
        "is_post_toss",
        "crossposted",
        "request_time",
        "submission_time",
        "p_a_computed",
        "converted_to_prediction",
    )
    readonly_fields = (
        "validation_errors",
        "crossposted",
        "crossposted_from",
        "p_a_computed",
        "request_time",
        "submission_time",
    )


class SubmissionFieldConfigInline(admin.TabularInline):
    model = SubmissionFieldConfig
    show_change_link = False
    extra = 0
    ordering = ("form_order",)


class GroupSubmissionsConfigAdmin(VersionAdmin):
    inlines = [SubmissionFieldConfigInline]
    list_filter = ("member_group", "tournament", "tournament_format")
    list_display = ("id", "__str__", "tournament_format")


class ControlledGroupSubmissionsConfigAdmin(VersionAdmin):
    inlines = [SubmissionFieldConfigInline]
    list_filter = ("member_group", "tournament", "tournament_format", "submission_type")
    list_display = (
        "id",
        "__str__",
        "tournament_format",
        "tournament",
        "submission_type",
        "active_from",
        "active_to",
    )

    def save_related(self, request, form, formsets, change):
        super(ControlledGroupSubmissionsConfigAdmin, self).save_related(
            request, form, formsets, change
        )

        for member_group in MemberGroup.objects.filter(
            tournaments__in=[form.instance.tournament]
        ):
            create_or_update_submission_config(member_group, form.instance)


class MemberTournamentPredictionAdmin(VersionAdmin):
    list_filter = ("member_group", "tournament__name", "prediction_format")
    list_display = (
        "member",
        "tournament",
        "member_group",
        "total_prediction_score",
        "grand_score",
    )

    actions = ("export_data_csv",)

    def export_data_csv(self, request, queryset):
        f = (
            "member__user__first_name",
            "member__user__last_name",
            "member_group__group__name",
            "grand_score",
            "total_prediction_score",
            "tournament_winning_team__name",
            "runner_up__name",
            "top_team_one__name",
            "top_team_two__name",
            "top_team_three__name",
            "top_team_four__name",
            "top_batsman_one__name",
            "top_batsman_two__name",
            "top_batsman_three__name",
            "top_bowler_one__name",
            "top_bowler_two__name",
            "top_bowler_three__name",
            "most_valuable_player_one__name",
            "most_valuable_player_two__name",
            "most_valuable_player_three__name",
        )
        view = PatchedCSVExportView(queryset=queryset, fields=f)
        return view.get(request)

    export_data_csv.short_description = "Export CSV for selected records"


class TouramentPredictionScoreAdmin(VersionAdmin):
    list_filter = ("prediction__member", "prediction__member_group")
    list_display = ("prediction", "rule", "points")


admin.site.register(MemberPrediction, MemberPredictionAdmin)
admin.site.register(
    PredictionSubmissionValidations, PredictionSubmissionValidationsAdmin
)
admin.site.register(PredictionScores, PredictionScoresAdmin)
admin.site.register(PostPredictionScores, PostPredictionScoresAdmin)
admin.site.register(MemberSubmission, MemberSubmissionAdmin)
admin.site.register(GroupSubmissionsConfig, GroupSubmissionsConfigAdmin)
admin.site.register(MemberTournamentPrediction, MemberTournamentPredictionAdmin)
admin.site.register(TouramentPredictionScore, TouramentPredictionScoreAdmin)
admin.site.register(
    ControlledGroupSubmissionsConfig, ControlledGroupSubmissionsConfigAdmin
)
