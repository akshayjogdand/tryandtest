from configurations.models import ConfigItem

from fixtures.models import TournamentDefaultRules


def get_default_tournament():
    return ConfigItem.objects.get(name="default_tournament").tournament


def get_default_tournament_rules(tournament):
    default_tournament_rules = TournamentDefaultRules.objects.get(
        tournament=tournament
    ).rules()

    return default_tournament_rules


def get_default_member_group():
    return ConfigItem.objects.get(name="default_member_group").member_group
