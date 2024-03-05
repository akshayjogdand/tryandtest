from DynamicContent.models import MessageBlock


def run(*args):
    for m in MessageBlock.objects.all():
        m.content_block = m.content_block.replace(
            "www.stumpguru.com", "www.fanaboard.com"
        )
        m.save()
