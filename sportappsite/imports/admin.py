from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import DataImport


class ImportAdmin(VersionAdmin):
    raw_id_fields = ("match",)
    autocomplete_lookup_fields = {"fk": ["match"]}
    readonly_fields = ("description",)
    list_filter = ("match", "member_group")


admin.site.register(DataImport, ImportAdmin)
