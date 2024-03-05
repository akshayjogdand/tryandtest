from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import FetchSeries, ScoreMatch, ScoreSeries


class FetchSeriesAdmin(VersionAdmin):
    readonly_fields = ("job_refs",)


class ScoreMatchAdmin(VersionAdmin):
    readonly_fields = ("job_refs",)
    list_filter = ("match__tournament",)


class ScoreSeriesAdmin(VersionAdmin):
    readonly_fields = ("job_refs",)
    list_filter = (
        "tournament",
        "series",
    )


admin.site.register(FetchSeries, FetchSeriesAdmin)
admin.site.register(ScoreMatch, ScoreMatchAdmin)
admin.site.register(ScoreSeries, ScoreSeriesAdmin)
