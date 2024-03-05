from .models import AppMedia
import drf_api


def get_media(filter_by, is_model=False):
    if len(filter_by):
        ams = AppMedia.objects.filter(**filter_by)
        if is_model:
            return ams
        return drf_api.serializers.AppMediaSerializer(ams, many=True).data
    else:
        return []
