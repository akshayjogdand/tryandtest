from django.contrib import admin

from django_summernote.admin import SummernoteModelAdmin

from .models import MessageBlock

# Register your models here.


class MessageBlockAdmin(SummernoteModelAdmin):
    list_display = (
        "id",
        "message_name",
        "tournament",
        "member",
        "member_group",
        "notes",
    )
    summernote_fields = ("content_block",)


admin.site.register(MessageBlock, MessageBlockAdmin)
