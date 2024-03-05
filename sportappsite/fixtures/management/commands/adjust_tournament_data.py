from datetime import timedelta

import logging

from django.core.management.base import BaseCommand

from fixtures.models import Match, Tournament

from django.db import transaction

from rules.models import DEFAULT_RULE_TYPES

from predictions.models import ControlledGroupSubmissionsConfig
from predictions.utils import clone_controlled_config

from ...models import TournamentDefaultRules, PlayerTournamentHistory

logger = logging.getLogger("auto_jobs")


def set_pth(tournament, series, match_type):
    logger.info(
        f"Setting Player Tournament History for {tournament}, match type={match_type}"
    )

    if match_type == Match.T_TWENTY:
        a_name = "t20_player"
    if match_type == Match.ONE_DAY:
        a_name = "odi_player"
    if match_type == Match.TEST:
        a_name = "test_player"

    for p in PlayerTournamentHistory.objects.filter(tournament=tournament):
        setattr(p, a_name, True)
        p.save()


def add_default_rules(tournament, series, match_type):
    logger.info(
        f"Creating Tournament Default Rules for: {tournament}, format={match_type}."
    )

    try:
        tdf = TournamentDefaultRules.objects.get(tournament=tournament)
    except TournamentDefaultRules.DoesNotExist:
        tdf = TournamentDefaultRules()
        tdf.tournament = tournament
        tdf.save()

    for master_rule_type in DEFAULT_RULE_TYPES:
        master_rules = master_rule_type.objects.filter(apply_to_match_type=match_type)
        tdf_attr = TournamentDefaultRules.METHOD_TO_ATTR_MAP[master_rule_type]
        for mr in master_rules:
            getattr(tdf, tdf_attr).add(mr)

    tdf.save()


def clone_from_similar(tournament, series_type, tournament_format):

    if ControlledGroupSubmissionsConfig.objects.filter(
        tournament=tournament, tournament_format=tournament_format
    ).exists():
        logger.info(
            f"Submission Configs for: {tournament}, format={tournament_format} already exist; skipping."
        )
        return

    filters = {
        series_type: True,
        "bi_lateral": tournament.bi_lateral,
    }

    similar_tournament = (
        Tournament.objects.filter(**filters)
        .exclude(id=tournament.id)
        .order_by("-id")
        .first()
    )

    if not similar_tournament:
        logger.error(
            f"Error creating Submission Configs for: {tournament}, format={tournament_format}."
            f"No similar past Tournament found with filters: {filters}"
        )
        return

    logger.info(f"Cloning Submissions Configs based on: {similar_tournament}")

    for cgcf in ControlledGroupSubmissionsConfig.objects.filter(
        tournament=similar_tournament, tournament_format=tournament_format
    ):
        c = clone_controlled_config(tournament, cgcf)
        logger.info(f"Created: {c}")


class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument(
            "--tournament-id", required=True, type=int, help="Tournament ID"
        )

    @transaction.atomic
    def handle(self, tournament_id, **kwargs):
        tournament = Tournament.objects.get(id=tournament_id)
        teams = set()
        match_dates = list()
        finish_in = 24
        clone_specs = set()

        for match in Match.objects.filter(tournament=tournament).order_by("match_date"):

            if "Test Match" in match.reference_name:
                tournament.test_series = True
                finish_in = 105
                clone_specs.add((tournament, "test_series", Match.TEST))

            elif "ODI Match" in match.reference_name:
                tournament.odi_series = True
                clone_specs.add((tournament, "odi_series", Match.ONE_DAY))

            elif "T20" in match.reference_name:
                tournament.t20_series = True
                clone_specs.add((tournament, "t20_series", Match.T_TWENTY))

            for t in match.teams():
                teams.add(t)

            match_dates.append(match.match_date)

        if len(teams) == 2:
            tournament.bi_lateral = True
            tournament.team_one = list(teams)[0]
            tournament.team_two = list(teams)[1]

        # This is not a bi-lateral Tournament, now need to rely on:
        # 1. Tournament config to get the types of Matches that will be played.
        # 2. Auto determine series from Match types.

        # 2 is attempted first, most likely 1 will not be needed

        else:
            logger.info(
                "Unable to determine Series from Match names, now attempting auto-discover from Match types."
            )
            tournament_series = tournament.series()
            if len(tournament_series) == 0:
                tournament_series = tournament.auto_discover_series()
                for (series, _) in tournament_series:
                    setattr(tournament, series, True)

            for series, match_type in tournament_series:
                clone_specs.add((tournament, series, match_type))

        for spec in clone_specs:
            clone_from_similar(*spec)
            add_default_rules(*spec)

        if len(clone_specs) == 1:
            set_pth(*list(clone_specs)[0])

        tournament.start_date = match_dates[0]
        tournament.end_date = match_dates[-1:][0] + timedelta(hours=finish_in)

        tournament.save()
