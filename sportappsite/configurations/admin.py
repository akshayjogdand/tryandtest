from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import ConfigItem, MatchSubmissionNotes, Feature


class ConfigItemAdmin(VersionAdmin):
    list_display = ("__str__", "value", "team", "tournament", "player", "member_group")


class MatchSubmissionNotesAdmin(VersionAdmin):
    list_display = ("name", "tournament")
    list_filter = ("matches",)
    filter_horizontal = ("matches",)


class FeatureAdmin(VersionAdmin):
    list_display = ("feature_type", "member_group", "enabled")
    list_filter = ("member_group",)
    # filter_horizontal = ("tournaments",)


admin.site.register(ConfigItem, ConfigItemAdmin)
admin.site.register(MatchSubmissionNotes, MatchSubmissionNotesAdmin)
admin.site.register(Feature, FeatureAdmin)
