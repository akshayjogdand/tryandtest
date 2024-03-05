from enum import IntEnum, unique

from configurations.models import ConfigItem

from members.models import MemberGroup


def draw_team():
    return ConfigItem.objects.get(name="draw_team").team


def tie_team():
    return ConfigItem.objects.get(name="tie_team").team


# Rename to tie team
def tournament_draw_team():
    return ConfigItem.objects.get(name="tournament_draw_team").team


def tournament_tie_team():
    return tournament_draw_team()


def control_group():
    return MemberGroup.objects.get(group__name="Control Group")


@unique
class MatchTypes(IntEnum):
    ONE_DAY = 1
    T_TWENTY = 2
    TEST = 3

    @classmethod
    def type_to_str(self, match_type):
        for t, s in self.type_choices():
            if t == match_type:
                return s

    @classmethod
    def type_to_series_str(self, match_type):
        if match_type == self.ONE_DAY.value:
            return "ODI series"
        if match_type == self.T_TWENTY.value:
            return "T-20 series"
        if match_type == self.TEST.value:
            return "Test series"

    @classmethod
    def type_choices(self):
        return (
            (self.ONE_DAY.value, "One Day"),
            (self.T_TWENTY.value, "T-20"),
            (self.TEST.value, "Test match"),
        )

    @classmethod
    def type_choices_str(self):
        l = []
        for v, s in self.type_choices():
            l.append("{}={}".format(s, v))

        return "\n".join(l)


@unique
class TournamentFormats(IntEnum):
    ONE_DAY = 1
    T_TWENTY = 2
    TEST = 3

    @classmethod
    def type_choices(self):
        return (
            (self.ONE_DAY.value, "One Day"),
            (self.T_TWENTY.value, "T-20"),
            (self.TEST.value, "Test match"),
        )

    @classmethod
    def type_choices_str(self):
        l = []
        for v, s in self.type_choices():
            l.append("{}={}".format(s, v))

        return "\n".join(l)


TournamentFormatToPTHAttrMapping = {
    TournamentFormats.T_TWENTY: "t20_player",
    TournamentFormats.ONE_DAY: "odi_player",
    TournamentFormats.TEST: "test_player",
}

TournamentSeriesAttributesToPTHAttrMapping = {
    "t20_series": "t20_player",
    "odi_series": "odi_player",
    "test_series": "test_player",
}
