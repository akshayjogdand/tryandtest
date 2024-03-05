from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import AppMedia

# Register your models here.


class AppMediaAdmin(VersionAdmin):
    list_display = (
        "media_name",
        "original_filename",
        "media_size",
        "media_type",
        "media_file",
        "media_note",
        "media_spec",
        "country",
        "team",
        "player",
    )
    readonly_fields = ["media_name", "original_filename"]
    list_filter = ["media_type", "media_size", "country", "team", "player"]
    search_fields = ["media_note"]


class AppMediaFieldConfigInline(admin.TabularInline):
    model = AppMedia
    fields = (
        "media_name",
        "original_filename",
        "media_size",
        "media_type",
        "media_file",
        "media_note",
        "media_spec",
    )
    readonly_fields = ["media_name", "original_filename"]
    show_change_link = False
    extra = 0


admin.site.register(AppMedia, AppMediaAdmin)
