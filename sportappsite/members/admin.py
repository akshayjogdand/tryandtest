from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import (
    Member,
    MemberGroup,
    MemberGroupRules,
    GroupLeaderBoard,
    LeaderBoardEntry,
    Membership,
    MemberGroupInvitation,
)

from app_media.admin import AppMediaFieldConfigInline


class MembershipInline(admin.TabularInline):
    model = Membership
    autocomplete_fields = ("member",)
    extra = 5


class MemberAdmin(VersionAdmin):
    list_display = ("id", "__str__", "joined", "email_verified")
    search_fields = (
        "user__first_name",
        "user__last_name",
    )
    inline = [AppMediaFieldConfigInline]


class MemberGroupAdmin(VersionAdmin):
    inlines = [MembershipInline]
    list_display = ("id", "__str__", "invitation_code")
    filter_horizontal = ("tournaments",)
    readonly_fields = ["invitation_code", "reserved"]


class MemberGroupRulesAdmin(VersionAdmin):
    filter_horizontal = (
        "group_post_match_prediction_scoring_rules",
        "group_submission_validation_rules",
        "group_prediction_scoring_rules",
        "group_player_scoring_rules",
        "group_leaderboard_scoring_rules",
    )


class LeaderBoardEntryInline(admin.TabularInline):
    model = LeaderBoardEntry
    can_delete = False
    show_change_link = False
    extra = 0
    readonly_fields = (
        "member",
        "previous_points",
        "this_match",
        "tournament_predictions_score",
        "total",
        "previous_position",
        "position_now",
        "rank_movement",
    )
    exclude = ("movement",)
    ordering = ("position_now",)


class GroupLeaderBoardAdmin(VersionAdmin):
    list_filter = ("board_number", "member_group", "match", "match__tournament")
    inlines = [
        LeaderBoardEntryInline,
    ]
    readonly_fields = ("member_group", "match", "board_number")
    list_display = ("id", "board_number", "member_group", "match")
    ordering = (
        "-id",
        "-board_number",
    )


class MemberGroupInvitationsAdmin(VersionAdmin):
    readonly_fields = ["invitation_code"]


class MembershipAdmin(VersionAdmin):
    list_filter = ("member_group",)
    list_display = (
        "id",
        "member",
        "member_group",
    )
    search_fields = (
        "member__user__first_name",
        "member__user__last_name",
        "member_group__group__name",
        "member__user__email",
    )
    # autocomplete_fields = ('member',)


admin.site.register(Member, MemberAdmin)
admin.site.register(MemberGroup, MemberGroupAdmin)
admin.site.register(MemberGroupRules, MemberGroupRulesAdmin)
admin.site.register(GroupLeaderBoard, GroupLeaderBoardAdmin)
admin.site.register(MemberGroupInvitation, MemberGroupInvitationsAdmin)
admin.site.register(Membership, MembershipAdmin)
