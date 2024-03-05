from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import (
    TournamentReward,
    TournamentRewardParticipant,
    TournamentRewardAgreement,
)


class TournamentRewardParticipantAdminInline(admin.TabularInline):
    model = TournamentRewardParticipant
    extra = 0
    can_delete = False
    show_change_link = False


class TouramentRewardAgreementAdminInLine(admin.TabularInline):
    model = TournamentRewardAgreement
    extra = 0
    can_delete = False
    show_change_link = False
    readonly_fields = ("admin_member", "date_agreed")
    fields = ("admin_member", "date_agreed")


class TournamentRewardAdmin(VersionAdmin):
    list_display = ("id", "member_group", "tournament")
    inlines = [
        TournamentRewardParticipantAdminInline,
        TouramentRewardAgreementAdminInLine,
    ]


admin.site.register(TournamentReward, TournamentRewardAdmin)
