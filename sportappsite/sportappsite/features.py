from configurations.models import Feature


def group_rewards_enabled(member_group):
    for f in member_group.features.all():
        if f.feature_type == Feature.FEATURE_GROUP_REWARDS:
            return f.enabled

    return False
