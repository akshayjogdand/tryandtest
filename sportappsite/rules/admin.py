from django.contrib import admin

from reversion.admin import VersionAdmin

from members.models import MemberGroupRules

from .models import (
    PlayerScoringMethod,
    PredictionScoringMethod,
    PredictionSubmissionValidationRule,
    PlayerScoringResult,
    PredictionScoringResult,
    PostMatchPredictionScoringMethod,
    PostMatchPredictionScoringMethodResult,
    TournamentScoringMethod,
    TournamentScoringMethodResult,
    GroupPlayerScoringResult,
    GroupPredictionScoringResult,
    GroupPlayerScoringMethod,
    GroupPredictionScoringMethod,
    GroupPredictionSubmissionValidationRule,
    GroupPostMatchPredictionScoringMethod,
    LeaderBoardScoringMethod,
    GroupLeaderBoardScoringMethod,
    GroupLeaderBoardScoringMethodResult,
    GroupTournamentScoringMethod,
    GroupTournamentScoringMethodResult,
    RuleRange,
    R1,
    R2,
)

RULE_ADMIN_LIST_DISPLAY = [
    "id",
    "name",
    "rule_category",
    "apply_to_match_type",
    "display_order",
    "variables",
    "calculation",
    "points_or_factor",
    "is_enabled",
    "is_default",
]

RULE_ADMIN_ORDERING = ("name",)

RULE_ADMIN_SEARCH_FIELDS = ["id", "name", "functions"]

RULE_ADMIN_LIST_FILTERS = ["name", "apply_to_match_type"]

RULE_ADMIN_READONLY_FIELDS = ["apply_rule_at"]

GROUP_RULE_ADMIN_READONLY_FIELDS = [
    "apply_rule_at",
    "is_default",
    "parent_rule",
    "apply_changes_to_cloned_rules",
]

GROUP_RULE_ADMIN_LIST_DISPLAY = RULE_ADMIN_LIST_DISPLAY.copy()
GROUP_RULE_ADMIN_LIST_DISPLAY.append("member_group")

GROUP_RULE_ADMIN_LIST_FILTERS = RULE_ADMIN_LIST_FILTERS.copy()


class R1Inline(admin.TabularInline):
    model = R1
    can_delete = True
    show_change_link = False
    extra = 0
    readonly_fields = ("rule",)


class R2Inline(admin.TabularInline):
    model = R2
    can_delete = True
    show_change_link = False
    extra = 0
    readonly_fields = ("rule",)


class PlayerScoringMethodAdmin(VersionAdmin):
    list_display = RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    search_fields = RULE_ADMIN_SEARCH_FIELDS
    list_filter = RULE_ADMIN_LIST_FILTERS
    _rof = RULE_ADMIN_READONLY_FIELDS.copy()
    _rof.append("enable_for_matches")
    readonly_fields = _rof
    inlines = [R1Inline]


class PredictionScoringMethodAdmin(VersionAdmin):
    list_display = RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    readonly_fields = RULE_ADMIN_READONLY_FIELDS
    search_fields = RULE_ADMIN_SEARCH_FIELDS
    list_filter = ["apply_to_match_type"]
    inlines = [R2Inline]


class PredictionSubmissionValidationRuleAdmin(VersionAdmin):
    list_display = RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    readonly_fields = RULE_ADMIN_READONLY_FIELDS
    list_filter = ["apply_to_match_type", "apply_to_submission_type"]


class PostMatchPredictionScoringMethodAdmin(VersionAdmin):
    list_display = RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    readonly_fields = RULE_ADMIN_READONLY_FIELDS
    search_fields = RULE_ADMIN_SEARCH_FIELDS
    list_filter = ["apply_to_match_type"]


class LeaderBoardScoringMethodAdmin(VersionAdmin):
    list_display = RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    readonly_fields = RULE_ADMIN_READONLY_FIELDS
    search_fields = RULE_ADMIN_SEARCH_FIELDS
    list_filter = ["apply_to_match_type"]


class TournamentScoringMethodAdmin(VersionAdmin):
    list_display = RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    readonly_fields = RULE_ADMIN_READONLY_FIELDS
    search_fields = RULE_ADMIN_SEARCH_FIELDS
    list_filter = ["apply_to_match_type"]


class PlayerScoringResultAdmin(VersionAdmin):
    readonly_fields = [
        "input_values",
        "calculation",
        "points_or_factor",
        "result",
        "rule",
    ]


class PredictionScoringResultAdmin(VersionAdmin):
    readonly_fields = [
        "input_values",
        "calculation",
        "points_or_factor",
        "result",
        "rule",
    ]


class PostMatchPredictionScoringMethodResultAdmin(VersionAdmin):
    readonly_fields = [
        "input_values",
        "calculation",
        "points_or_factor",
        "result",
        "rule",
    ]


class TournamentScoringMethodResultAdmin(VersionAdmin):
    readonly_fields = [
        "input_values",
        "calculation",
        "points_or_factor",
        "result",
        "rule",
    ]


class MemberGroupListFilter(admin.SimpleListFilter):
    title = "Member Group"
    parameter_name = "mgrp"

    def lookups(self, request, model_admin):
        selections = []

        for o in MemberGroupRules.objects.all():
            selections.append((o.id, o.member_group.group.name))

        return selections

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(membergrouprules__id=int(self.value()))
        else:
            return queryset


GROUP_RULE_ADMIN_LIST_FILTERS.append(MemberGroupListFilter)


class GroupPlayerScoringMethodAdmin(VersionAdmin):
    list_display = GROUP_RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    search_fields = RULE_ADMIN_SEARCH_FIELDS
    list_filter = GROUP_RULE_ADMIN_LIST_FILTERS
    _rof = GROUP_RULE_ADMIN_READONLY_FIELDS.copy()
    _rof.append("enable_for_matches")
    readonly_fields = _rof

    def member_group(self, obj):
        mg = obj.membergrouprules_set.all().first()
        if mg is not None:
            return mg.member_group.group.name
        else:
            return "-"


class GroupPredictionScoringMethodAdmin(VersionAdmin):
    list_display = GROUP_RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    readonly_fields = GROUP_RULE_ADMIN_READONLY_FIELDS
    search_fields = RULE_ADMIN_SEARCH_FIELDS
    list_filter = GROUP_RULE_ADMIN_LIST_FILTERS

    def member_group(self, obj):
        mg = obj.membergrouprules_set.all().first()
        if mg is not None:
            return mg.member_group.group.name
        else:
            return "-"


class GroupPredictionSubmissionValidationRuleAdmin(VersionAdmin):
    list_display = GROUP_RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    readonly_fields = GROUP_RULE_ADMIN_READONLY_FIELDS
    list_filter = GROUP_RULE_ADMIN_LIST_FILTERS

    def member_group(self, obj):
        mg = obj.membergrouprules_set.all().first()
        if mg is not None:
            return mg.member_group.group.name
        else:
            return "-"


class GroupPostMatchPredictionScoringMethodAdmin(VersionAdmin):
    list_display = GROUP_RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    readonly_fields = GROUP_RULE_ADMIN_READONLY_FIELDS
    search_fields = RULE_ADMIN_SEARCH_FIELDS
    list_filter = GROUP_RULE_ADMIN_LIST_FILTERS

    def member_group(self, obj):
        mg = obj.membergrouprules_set.all().first()
        if mg is not None:
            return mg.member_group.group.name
        else:
            return "-"


class GroupLeaderBoardScoringMethodAdmin(VersionAdmin):
    list_display = GROUP_RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    readonly_fields = GROUP_RULE_ADMIN_READONLY_FIELDS
    search_fields = RULE_ADMIN_SEARCH_FIELDS
    list_filter = GROUP_RULE_ADMIN_LIST_FILTERS

    def member_group(self, obj):
        mg = obj.membergrouprules_set.all().first()
        if mg is not None:
            return mg.member_group.group.name
        else:
            return "-"


class GroupTournamentScoringMethodAdmin(VersionAdmin):
    list_display = GROUP_RULE_ADMIN_LIST_DISPLAY
    ordering = RULE_ADMIN_ORDERING
    readonly_fields = GROUP_RULE_ADMIN_READONLY_FIELDS
    search_fields = RULE_ADMIN_SEARCH_FIELDS
    list_filter = GROUP_RULE_ADMIN_LIST_FILTERS

    def member_group(self, obj):
        mg = obj.membergrouprules_set.all().first()
        if mg is not None:
            return mg.member_group.group.name
        else:
            return "-"


class GroupPlayerScoringResultAdmin(VersionAdmin):
    readonly_fields = [
        "input_values",
        "calculation",
        "points_or_factor",
        "result",
        "rule",
    ]


class GroupPredictionScoringResultAdmin(VersionAdmin):
    readonly_fields = [
        "input_values",
        "calculation",
        "points_or_factor",
        "result",
        "rule",
    ]


class GroupPostMatchPredictionScoringMethodResultAdmin(VersionAdmin):
    readonly_fields = [
        "input_values",
        "calculation",
        "points_or_factor",
        "result",
        "rule",
    ]


class GroupLeaderBoardScoringMethodResultAdmin(VersionAdmin):
    readonly_fields = [
        "input_values",
        "calculation",
        "points_or_factor",
        "result",
        "rule",
    ]


class GroupTournamentScoringMethodResultAdmin(VersionAdmin):
    readonly_fields = [
        "input_values",
        "calculation",
        "points_or_factor",
        "result",
        "rule",
    ]


admin.site.register(PlayerScoringMethod, PlayerScoringMethodAdmin)
admin.site.register(PredictionScoringMethod, PredictionScoringMethodAdmin)
admin.site.register(
    PredictionSubmissionValidationRule, PredictionSubmissionValidationRuleAdmin
)
admin.site.register(PlayerScoringResult, PlayerScoringResultAdmin)
admin.site.register(PredictionScoringResult, PredictionScoringResultAdmin)
admin.site.register(
    PostMatchPredictionScoringMethod, PostMatchPredictionScoringMethodAdmin
)
admin.site.register(
    PostMatchPredictionScoringMethodResult, PostMatchPredictionScoringMethodResultAdmin
)
admin.site.register(LeaderBoardScoringMethod, LeaderBoardScoringMethodAdmin)
admin.site.register(TournamentScoringMethod, TournamentScoringMethodAdmin)

admin.site.register(GroupLeaderBoardScoringMethod, GroupLeaderBoardScoringMethodAdmin)
admin.site.register(GroupPlayerScoringMethod, GroupPlayerScoringMethodAdmin)
admin.site.register(GroupPredictionScoringMethod, GroupPredictionScoringMethodAdmin)
admin.site.register(
    GroupPredictionSubmissionValidationRule,
    GroupPredictionSubmissionValidationRuleAdmin,
)
admin.site.register(
    GroupPostMatchPredictionScoringMethod, GroupPostMatchPredictionScoringMethodAdmin
)
admin.site.register(GroupTournamentScoringMethod, GroupTournamentScoringMethodAdmin)

admin.site.register(GroupPlayerScoringResult, GroupPlayerScoringResultAdmin)
admin.site.register(GroupPredictionScoringResult, GroupPredictionScoringResultAdmin)
admin.site.register(
    GroupLeaderBoardScoringMethodResult, GroupLeaderBoardScoringMethodResultAdmin
)
admin.site.register(
    GroupTournamentScoringMethodResult, GroupTournamentScoringMethodResultAdmin
)
