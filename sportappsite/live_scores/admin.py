from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import Properties, BallByBall


class PropertiesAdmin(VersionAdmin):
    # readonly_fields = ('player', 'team', 'tournament', 'squad', 'match')
    list_display = (
        "property_value",
        "property_name",
        "property_context",
        "player",
        "team",
        "tournament",
        "squad",
        "match",
    )
    list_filter = ["player", "match", "tournament"]


class BallByBallAdmin(VersionAdmin):
    readonly_fields = (
        "match",
        "over",
        "ball",
        "batsman",
        "bowler",
        "fielders",
        "wicket",
        "runs",
        "fours",
        "sixes",
        "dot_ball",
        "extras",
        "wicket_type",
        "last_ball_of_over",
        "comments",
    )
    list_display = (
        "id",
        "match",
        "over",
        "ball",
        "batsman",
        "batting_team",
        "bowler",
        "bowling_team",
        "fielders",
        "wicket",
        "runs",
        "fours",
        "sixes",
        "dot_ball",
        "ball_type",
        "extras",
        "wicket_type",
        "last_ball_of_over",
    )
    list_filter = (
        "match",
        "batting_team",
        "bowling_team",
        "over",
        "batsman",
        "bowler",
        "ball_type",
    )


admin.site.register(Properties, PropertiesAdmin)
admin.site.register(BallByBall, BallByBallAdmin)
