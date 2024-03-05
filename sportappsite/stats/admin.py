from django.contrib import admin

from reversion.admin import VersionAdmin

import easy

from scoring.utils import rule_results_as_table

from .models import (
    PlayerStat,
    TeamStat,
    PredictionFieldStat,
    BattingPerformance,
    BowlingPerformance,
    FieldingPerformance,
    MatchPerformance,
    PlayerScores,
)

PERF_ADMIN_LIST_FILTER = (
    "player__name",
    "match__name",
    "team__name",
    "match__tournament",
)

PERF_ADMIN_RAW_ID_FIELDS = ["player", "match", "team"]

PERF_ADMIN_AUTOCOMPLETE_FIELDS = {"fk": ["player", "match", "team"]}

PERF_ADMIN_SEARCH_FIELDS = ["player__name", "match__name", "id"]

PERF_ADMIN_LIST_DISPLAY_FIELDS = ["id", "player", "team", "match"]

PERF_ADMIN_READ_ONLY_FIELDS = [
    "stat_name",
    "stat_value",
    "stat_index",
    "stat_unit",
    "match",
    "team",
    "tournament",
    "is_latest",
]


class PlayerStatAdmin(VersionAdmin):
    _r = PERF_ADMIN_RAW_ID_FIELDS.copy()
    raw_id_fields = _r
    _a = PERF_ADMIN_AUTOCOMPLETE_FIELDS.copy()
    _a["fk"].append("stat_name")
    autocomplete_lookup_fields = _a
    _s = PERF_ADMIN_SEARCH_FIELDS.copy()
    _s.extend(("stat_name", "tournament__name"))
    search_fields = _s
    _l = PERF_ADMIN_LIST_DISPLAY_FIELDS.copy()
    _f = PERF_ADMIN_LIST_DISPLAY_FIELDS.copy()
    _l.extend(
        [
            "id",
            "tournament",
            "stat_name",
            "stat_index",
            "stat_value",
            "member_group",
            "is_latest",
            "computed_on",
        ]
    )
    _f.extend(["tournament", "stat_name", "member_group"])
    list_filter = _f
    list_display = _l


class TeamStatAdmin(VersionAdmin):
    _r = PERF_ADMIN_RAW_ID_FIELDS.copy()
    _r.remove("player")

    _a = PERF_ADMIN_AUTOCOMPLETE_FIELDS.copy()
    _a["fk"].append("stat_name")
    autocomplete_lookup_fields = _a
    _s = PERF_ADMIN_SEARCH_FIELDS.copy()
    _s.extend(("stat_name", "tournament__name"))
    search_fields = _s
    _l = PERF_ADMIN_LIST_DISPLAY_FIELDS.copy()
    _f = PERF_ADMIN_LIST_DISPLAY_FIELDS.copy()
    _l.extend(
        [
            "tournament",
            "stat_name",
            "stat_index",
            "stat_value",
            "member_group",
            "is_latest",
            "computed_on",
        ]
    )
    _f.extend(["tournament", "stat_name", "member_group"])
    _l.remove("player")
    _f.remove("player")

    list_filter = _f
    raw_id_fields = _r
    list_display = _l


class BattingPerformanceAdmin(VersionAdmin):
    _r = PERF_ADMIN_RAW_ID_FIELDS.copy()
    _r.append("bowler")
    raw_id_fields = _r
    _a = PERF_ADMIN_AUTOCOMPLETE_FIELDS.copy()
    _a["fk"].append("bowler")
    autocomplete_lookup_fields = _a
    search_fields = PERF_ADMIN_SEARCH_FIELDS
    list_filter = PERF_ADMIN_LIST_FILTER
    _l = PERF_ADMIN_LIST_DISPLAY_FIELDS.copy()
    _l.extend(
        [
            "innings",
            "position",
            "runs",
            "balls",
            "fours",
            "sixes",
            "was_out",
            "strike_rate",
            "dismissal",
        ]
    )
    list_display = _l
    filter_horizontal = ("fielder",)


class BowlingPerformanceAdmin(VersionAdmin):
    raw_id_fields = PERF_ADMIN_RAW_ID_FIELDS
    autocomplete_lookup_fields = PERF_ADMIN_AUTOCOMPLETE_FIELDS
    list_filter = PERF_ADMIN_LIST_FILTER
    search_fields = PERF_ADMIN_SEARCH_FIELDS
    _l = PERF_ADMIN_LIST_DISPLAY_FIELDS.copy()
    _l.extend(
        [
            "innings",
            "overs",
            "balls",
            "maiden",
            "runs",
            "wickets",
            "extras",
            "dot_balls",
            "fours",
            "sixes",
            "hat_tricks",
            "economy",
        ]
    )
    list_display = _l


class FieldingPerformanceAdmin(VersionAdmin):
    raw_id_fields = PERF_ADMIN_RAW_ID_FIELDS
    autocomplete_lookup_fields = PERF_ADMIN_AUTOCOMPLETE_FIELDS
    search_fields = PERF_ADMIN_SEARCH_FIELDS
    list_filter = PERF_ADMIN_LIST_FILTER
    _l = PERF_ADMIN_LIST_DISPLAY_FIELDS.copy()
    _l.extend(["innings", "catches", "stumpings", "runouts"])
    list_display = _l


class MatchPerformanceAdmin(VersionAdmin):
    raw_id_fields = PERF_ADMIN_RAW_ID_FIELDS
    autocomplete_lookup_fields = PERF_ADMIN_AUTOCOMPLETE_FIELDS
    list_filter = PERF_ADMIN_LIST_FILTER
    search_fields = PERF_ADMIN_SEARCH_FIELDS
    _l = PERF_ADMIN_LIST_DISPLAY_FIELDS.copy()
    _l.extend(
        [
            "last_run",
            "last_wicket",
            "man_of_the_match",
            "max_fours_hit",
            "max_sixes_hit",
            "is_captain",
            "is_wicketkeeper",
            "most_runs",
            "most_wickets",
        ]
    )
    list_display = _l


class PlayerScoresAdmin(VersionAdmin):
    readonly_fields = ("player", "match", "total_score", "team", "results_as_table")
    list_display = (
        "player",
        "match",
        "team",
        "total_score",
    )
    list_filter = PERF_ADMIN_LIST_FILTER
    search_fields = ("player__name", "match__name", "id")
    exclude = ("detailed_scoring",)

    @easy.with_tags()
    @easy.short(desc="Scoring", tags=True)
    def results_as_table(self, instance):
        return rule_results_as_table(instance.detailed_scoring.all())


class PredictionFieldStatAdmin(VersionAdmin):
    _ro = PERF_ADMIN_READ_ONLY_FIELDS.copy()
    _ro.extend(
        ["match_or_tournament_format", "member_group",]
    )
    readonly_fields = _ro

    _r = PERF_ADMIN_RAW_ID_FIELDS.copy()
    _r.remove("player")
    raw_id_fields = _r

    _a = PERF_ADMIN_AUTOCOMPLETE_FIELDS.copy()
    _a["fk"].append("stat_name")
    autocomplete_lookup_fields = _a

    _s = PERF_ADMIN_SEARCH_FIELDS.copy()
    _s.extend(("stat_name", "tournament__name"))
    search_fields = _s

    _l = PERF_ADMIN_LIST_DISPLAY_FIELDS.copy()
    _l.remove("player")

    _l.extend(
        [
            "tournament",
            "stat_name",
            "stat_index",
            "raw_input_value",
            "stat_value",
            "member_group",
            "is_latest",
            "computed_on",
        ]
    )
    list_display = _l

    _f = PERF_ADMIN_LIST_DISPLAY_FIELDS.copy()
    _f.extend(["tournament", "stat_name", "member_group"])
    _f.remove("player")
    list_filter = _f


admin.site.register(BattingPerformance, BattingPerformanceAdmin)
admin.site.register(BowlingPerformance, BowlingPerformanceAdmin)
admin.site.register(FieldingPerformance, FieldingPerformanceAdmin)
admin.site.register(MatchPerformance, MatchPerformanceAdmin)
admin.site.register(PlayerScores, PlayerScoresAdmin)
admin.site.register(PlayerStat, PlayerStatAdmin)
admin.site.register(TeamStat, TeamStatAdmin)
admin.site.register(PredictionFieldStat, PredictionFieldStatAdmin)
