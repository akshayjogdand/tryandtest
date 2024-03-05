from prettytable import PrettyTable

from django.db import transaction

from django.core.management.base import BaseCommand, CommandError

from fixtures.models import Player, Match

from .utils import get_or_score_player_performance


class Command(BaseCommand):
    help = "Score a single Players performance in a given Match"

    def add_arguments(self, parser):
        parser.add_argument("--player-id", type=int, required=True, help="Player ID")
        parser.add_argument("--match-id", type=int, required=True, help="Match ID")
        parser.add_argument(
            "--re-score",
            action="store_true",
            required=False,
            help="Re-score this performance, if already scored.",
        )
        parser.add_argument(
            "--no-print",
            action="store_true",
            required=False,
            help="Don't print results. Default is to print.",
        )

    @transaction.atomic
    def handle(self, player_id, match_id, re_score, no_print, *args, **options):
        try:
            match = Match.objects.get(id=match_id)
            player = Player.objects.get(id=player_id)

            player_scores = get_or_score_player_performance(player, match, re_score)

            if player_scores and not no_print:
                table = PrettyTable()
                table.field_names = [
                    "Scoring method",
                    "Points/Factor",
                    "Input values",
                    "Scoring result",
                ]

                for result in player_scores.detailed_scoring.all():
                    table.add_row(
                        [
                            "{}(id={})".format(result.rule.name, result.rule.id),
                            result.points_or_factor,
                            result.input_values,
                            result.result,
                        ]
                    )

                print(
                    "\nPlayer: {}\nMatch no:[{}]: {}".format(
                        player.name, match.match_number, match.name
                    )
                )
                print(table)
                print("Total score: [ {} ]".format(player_scores.total_score))

        except Player.DoesNotExist:
            raise CommandError("Player with ID: {} not found.".format(player_id))
        except Match.DoesNotExist:
            raise CommandError("Match with ID: {} not found.".format(match_id))
        except Exception as e:
            raise e
