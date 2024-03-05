from prettytable import PrettyTable

from django.core.management.base import BaseCommand, CommandError

from django.db import transaction

from fixtures.models import Match

from scoring.utils import get_or_score_match_player_performances


class Command(BaseCommand):
    help = """Score all Players performance in a given Match and
              optionally also score Predictions"""

    def add_arguments(self, parser):
        parser.add_argument("--match-id", type=int, required=True, help="Match ID")
        parser.add_argument(
            "--re-score",
            action="store_true",
            required=False,
            help="If the match has been scored, re-score",
        )
        parser.add_argument(
            "--no-print",
            action="store_true",
            required=False,
            help="Don't print results. Default is to print.",
        )

    @transaction.atomic
    def handle(self, match_id, re_score, no_print, *args, **options):
        try:
            match = Match.objects.get(id=match_id)
            match_scores = get_or_score_match_player_performances(match, re_score)

            if not no_print:
                table = PrettyTable()
                table.field_names = [
                    "Player",
                    "Scoring method",
                    "Points/Factor",
                    "Input values",
                    "Scoring result",
                    "Total",
                ]

                for player, player_score in match_scores.items():
                    for score in player_score.detailed_scoring.all():
                        table.add_row(
                            [
                                player.name,
                                "{}(id={})".format(score.rule.name, score.rule.id),
                                score.points_or_factor,
                                score.input_values,
                                score.result,
                                "-",
                            ]
                        )

                    table.add_row(
                        [player.name]
                        + ["-" for i in range(len(table.field_names) - 2)]
                        + [player_score.total_score]
                    )

                    table.add_row(["" for i in range(len(table.field_names))])

                print("\nMatch number: {}, {}".format(match.match_number, match.name))
                print(table)

        except Match.DoesNotExist:
            raise CommandError("Match with ID: {} not found.".format(match_id))
        except Exception as e:
            raise e
