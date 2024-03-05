import operator
import itertools

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from fixtures.models import Player, Match, Tournament
from stats.models import PlayerStat, PlayerScores


def remove_old_records(match):
    for ps in PlayerStat.objects.filter(tournament=match.tournament):
        ps.delete()


def top_scoring_players_in_tournament(match):
    tournament = match.tournament
    stat_name = "top_scoring_players_in_tournament"

    player_scores = PlayerScores.objects.filter(
        match__match_status=Match.COMPLETED, match__tournament=tournament
    )

    if not player_scores.exists():
        return

    tally = dict()
    for ps in player_scores:
        if ps.player not in tally:
            tally[ps.player] = {
                "player": ps.player,
                "team": ps.team,
                "tournament_total": ps.total_score,
            }
        else:
            current_total = tally[ps.player].get("tournament_total")
            tally[ps.player].update(
                {"tournament_total": current_total + ps.total_score}
            )

    top_five = sorted(
        tally.values(), reverse=True, key=operator.itemgetter("tournament_total")
    )[:5]

    for s in PlayerStat.objects.filter(
        stat_name=stat_name, tournament=tournament, is_latest=True
    ):
        s.is_latest = False
        s.save()

    for i, score in enumerate(top_five, 1):
        ps = PlayerStat()
        ps.player = score["player"]
        ps.team = score["team"]
        ps.match = match
        ps.tournament = tournament
        ps.stat_name = stat_name
        ps.stat_index = i
        ps.stat_value = score["tournament_total"]
        ps.is_latest = True
        ps.save()


def top_scoring_players_in_past_matches(tournament, limit_to_matches=2):
    matches = (
        Match.objects.filter(tournament=tournament, match_status=Match.COMPLETED)
        .exclude(match_result=Match.MR_ABANDONED)
        .order_by("-match_date")
    )
    data = []
    stat_name = "top_scoring_players_in_past_matches"

    # Need to do this as last <limit_to_matches>
    # Matches might be complete but not scored
    count = 0
    for match in matches:
        if count < limit_to_matches:
            player_scores = PlayerScores.objects.filter(match=match).order_by(
                "-total_score"
            )
            if player_scores.exists():
                data.extend(
                    sorted(player_scores, key=lambda ps: ps.total_score, reverse=True)[
                        :3
                    ]
                )
                count = count + 1
        else:
            break

    for s in PlayerStat.objects.filter(
        stat_name=stat_name, tournament=tournament, is_latest=True
    ):
        s.is_latest = False
        s.save()

    for match, ps_list in itertools.groupby(data, key=operator.attrgetter("match")):
        for i, score in enumerate(ps_list, 1):
            ps = PlayerStat()
            ps.player = score.player
            ps.team = score.team
            ps.match = match
            ps.tournament = tournament
            ps.stat_name = stat_name
            ps.stat_index = i
            ps.stat_value = score.total_score
            ps.is_latest = True
            ps.save()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--match-id",
            required=True,
            type=int,
            help="Match ID for which stats have to be computed.",
        )

        parser.add_argument(
            "--delete-previous",
            required=False,
            action="store_true",
            default=False,
            help="Clear all stats for the Tournament prior to calculating.",
        )

    @transaction.atomic
    def handle(self, match_id, delete_previous, *args, **kwargs):

        try:
            match = Match.objects.get(id=match_id)
            if delete_previous:
                remove_old_records(match)

        except Match.DoesNotExist:
            raise CommandError("Match with that ID does not exist.")

        top_scoring_players_in_tournament(match)
        top_scoring_players_in_past_matches(match.tournament)
