from django.contrib import admin
from reversion.admin import VersionAdmin
from .models import (
    Tournament,
    Country,
    Team,
    Player,
    Squad,
    City,
    Venue,
    Match,
    Club,
    PlayerTournamentHistory,
    TournamentDefaultRules,
)

from app_media.admin import AppMediaFieldConfigInline
from .models import (
    Tournament,
    Country,
    Team,
    Player,
    Squad,
    City,
    Venue,
    Match,
    Club,
    PlayerTournamentHistory,
    TournamentDefaultRules,
    PlayingSquad,
    PlayerSquadInfo,
)


class ClubAdmin(VersionAdmin):
    pass


class TournamentAdmin(VersionAdmin):
    list_display = ["id", "name", "abbreviation", "start_date", "end_date"]
    inlines = [AppMediaFieldConfigInline]


class CountryAdmin(VersionAdmin):
    filter_horizontal = ("timezones",)
    inlines = [AppMediaFieldConfigInline]


class TeamAdmin(VersionAdmin):
    inlines = [AppMediaFieldConfigInline]
    list_display = ["id", "name"]
    ordering = ("name",)


class PlayerTournamentAdminInline(admin.TabularInline):
    model = PlayerTournamentHistory
    extra = 0
    can_delete = False
    show_change_link = False
    readonly_fields = ("tournament", "team")


class PlayerAdmin(VersionAdmin):
    search_fields = ("name",)
    list_display = ["id", "name", "country", "born"]
    ordering = ("name",)
    inlines = [PlayerTournamentAdminInline, AppMediaFieldConfigInline]


class SquadAdmin(VersionAdmin):
    filter_horizontal = ("players",)
    list_display = ["id", "__str__"]
    ordering = ("-id",)
    search_fields = ("team__name", "matches_played", "id", "squad_number")
    readonly_fields = ("id", "matches_played")


class CityAdmin(VersionAdmin):
    ordering = ("name",)
    list_display = ["id", "__str__"]


class VenueAdmin(VersionAdmin):
    ordering = ("name",)
    list_display = ["id", "__str__"]


class MatchAdmin(VersionAdmin):
    readonly_fields = (
        "id",
        "name",
        "reference_name",
        "short_display_name",
        "calculated_winning_score",
        "winning_score",
    )
    search_fields = ("match_number", "name", "reference_name", "match_number")
    list_display = (
        "id",
        "name",
        "match_number",
        "match_date",
        "tournament",
        "reference_name",
    )
    list_filter = ("tournament",)
    ordering = ("-tournament", "match_number")
    fields = (
        "id",
        "submissions_allowed",
        "post_toss_changes_allowed",
        "reference_name",
        "short_display_name",
        "fake_match",
        "name",
        "tournament",
        "venue",
        "match_date",
        "match_number",
        "match_type",
        "match_status",
        "match_result",
        "toss_winner",
        "toss_outcome",
        "toss_time",
        "match_start_time",
        "toss_decision",
        "team_one",
        "team_two",
        "first_wicket_gone_in_over",
        "first_innings_runs",
        "first_innings_overs",
        "first_innings_balls",
        "first_innings_wickets",
        "first_innings_fours",
        "first_innings_sixes",
        "first_innings_extras",
        "first_innings_noballs",
        "first_innings_wides",
        "first_innings_byes",
        "first_innings_legbyes",
        "first_innings_penalties",
        "first_innings_free_hits",
        "first_innings_bowled",
        "first_innings_lbws",
        "first_innings_catches",
        "first_innings_stumpings",
        "first_innings_runouts",
        "second_innings_runs",
        "second_innings_overs",
        "second_innings_balls",
        "second_innings_wickets",
        "second_innings_fours",
        "second_innings_sixes",
        "second_innings_extras",
        "second_innings_noballs",
        "second_innings_wides",
        "second_innings_byes",
        "second_innings_legbyes",
        "second_innings_penalties",
        "second_innings_catches",
        "second_innings_stumpings",
        "second_innings_free_hits",
        "second_innings_bowled",
        "second_innings_lbws",
        "third_innings_runs",
        "third_innings_overs",
        "third_innings_balls",
        "third_innings_wickets",
        "third_innings_fours",
        "third_innings_sixes",
        "third_innings_extras",
        "third_innings_noballs",
        "third_innings_wides",
        "third_innings_byes",
        "third_innings_legbyes",
        "third_innings_penalties",
        "third_innings_catches",
        "third_innings_stumpings",
        "third_innings_free_hits",
        "third_innings_bowled",
        "third_innings_lbws",
        "third_innings_runouts",
        "fourth_innings_runs",
        "fourth_innings_overs",
        "fourth_innings_balls",
        "fourth_innings_wickets",
        "fourth_innings_fours",
        "fourth_innings_sixes",
        "fourth_innings_extras",
        "fourth_innings_noballs",
        "fourth_innings_wides",
        "fourth_innings_byes",
        "fourth_innings_legbyes",
        "fourth_innings_penalties",
        "fourth_innings_catches",
        "fourth_innings_stumpings",
        "fourth_innings_free_hits",
        "fourth_innings_bowled",
        "fourth_innings_lbws",
        "fourth_innings_runouts",
        "maximum_overs",
        "maximum_overs_balls",
        "final_overs",
        "final_overs_balls",
        "bonus_value",
        "bonus_applicable",
        "win_margin_runs",
        "winning_score",
        "calculated_winning_score",
        "final_winning_score",
        "bat_first_team",
        "winning_team",
        "super_over_played",
        "super_over_winner",
        "max_fours_by",
        "max_sixes_by",
        "most_runs_by",
        "most_wickets_by",
        "dl_applicable",
        "dl_overs",
        "dl_overs_balls",
        "dl_target",
        "dl_calculated_winning_score",
    )

    filter_horizontal = (
        "max_fours_by",
        "max_sixes_by",
        "most_runs_by",
        "most_wickets_by",
    )


class PlayerTournamentHistoryAdmin(VersionAdmin):
    list_filter = ("player", "tournament", "team", "status")
    list_display = (
        "__str__",
        "player",
        "tournament",
        "team",
        "t20_player",
        "odi_player",
        "test_player",
    )
    ordering = ("team",)


class TournamentDefaultRulesAdmin(VersionAdmin):
    filter_horizontal = (
        "tournament_post_predictions_scoring_methods",
        "tournament_prediction_validation_rules",
        "tournament_prediction_scoring_method",
        "tournament_player_scoring_method",
        "tournament_leaderboard_scoring_methods",
    )


# live_scores changes: Added PlayerSuadInfoInline, PlayingSquadAdmin
class PlayerSquadInfoInline(admin.TabularInline):
    model = PlayerSquadInfo
    fields = ("player", "player_skill", "player_role")
    raw_id_fields = [
        "player",
    ]
    autocomplete_lookup_fields = {"fk": ["player"]}
    extra = 5


class PlayingSquadAdmin(VersionAdmin):
    inlines = [PlayerSquadInfoInline]
    list_display = ("match", "team_tournament")


admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Squad, SquadAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Venue, VenueAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Club, ClubAdmin)
admin.site.register(PlayerTournamentHistory, PlayerTournamentHistoryAdmin)
admin.site.register(TournamentDefaultRules, TournamentDefaultRulesAdmin)
# live_scores changes: Added PlayingSquadInfo
admin.site.register(PlayingSquad, PlayingSquadAdmin)
