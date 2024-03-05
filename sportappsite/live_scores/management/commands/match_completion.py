import logging

import pycricket

from django.core.management.base import BaseCommand

from django.db.models import Sum, Max, Q

from django.db import transaction

from collections import defaultdict

from fixtures.models import Match, Player, PlayerTournamentHistory

from stats.models import MatchPerformance, BattingPerformance, BowlingPerformance

from live_scores.models import Properties, BallByBall

# pending things are stumpings, catches, runouts, bowled

logger = logging.getLogger("live_scores.ball_by_ball")


def find_highest(player_stats, stat_name):
    highest_value = 0
    highest_players = list()

    for player, stats in player_stats.items():
        for name, value in stats.items():
            if name == stat_name:
                if value:
                    if value == highest_value:
                        highest_players.append(player)
                    if value > highest_value:
                        highest_value = value
                        highest_players.clear()
                        highest_players.append(player)

    return highest_players


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("match_key", nargs="+", type=str)

    def update_match_performance(self, match, team, player, attribute, value):
        try:
            mp = MatchPerformance.objects.get(match=match, player=player)
        except MatchPerformance.DoesNotExist:
            mp = MatchPerformance()
            mp.player = player
            mp.match = match
            mp.tournament = match.tournament
            mp.team = team

        setattr(mp, attribute, value)
        mp.save()

    def update_innings_info(
        self, match, active_match_info, team_innings, innings_property
    ):

        try:
            setattr(
                match,
                innings_property + "_runs",
                int(active_match_info["data"]["card"]["innings"][team_innings]["runs"]),
            )
            setattr(
                match,
                innings_property + "_overs",
                int(
                    active_match_info["data"]["card"]["innings"][team_innings][
                        "overs"
                    ].split(".")[0]
                ),
            )
            setattr(
                match,
                innings_property + "_balls",
                int(
                    active_match_info["data"]["card"]["innings"][team_innings][
                        "overs"
                    ].split(".")[1]
                ),
            )
            setattr(
                match,
                innings_property + "_wickets",
                int(
                    active_match_info["data"]["card"]["innings"][team_innings][
                        "wickets"
                    ]
                ),
            )
            setattr(
                match,
                innings_property + "_noballs",
                int(
                    active_match_info["data"]["card"]["innings"][team_innings]["noball"]
                ),
            )
            setattr(
                match,
                innings_property + "_wides",
                int(active_match_info["data"]["card"]["innings"][team_innings]["wide"]),
            )
            setattr(
                match,
                innings_property + "_fours",
                int(
                    active_match_info["data"]["card"]["innings"][team_innings]["fours"]
                ),
            )
            setattr(
                match,
                innings_property + "_sixes",
                int(
                    active_match_info["data"]["card"]["innings"][team_innings]["sixes"]
                ),
            )
            setattr(
                match,
                innings_property + "_byes",
                int(active_match_info["data"]["card"]["innings"][team_innings]["bye"]),
            )
            setattr(
                match,
                innings_property + "_legbyes",
                int(
                    active_match_info["data"]["card"]["innings"][team_innings]["legbye"]
                ),
            )

        except Exception as ex:
            logger.exception(
                f"Error settings innings properties for: {match}, innings={innings_property}, skipping."
            )

    @transaction.atomic
    def handle(self, *args, **options):
        handler = pycricket.RcaStorageHandler()
        start = pycricket.RcaApp(
            access_key="eed6178168b033260de5884da95eebb5",
            secret_key="0d1cda0c712d0b861841765a9c5673d4",
            app_id="2208",
            store_handler=handler,
        )

        match_key = options["match_key"][0]
        active_match_info = start.get_match(match_key)
        match_keys = Properties.get_obj_cricketapi(match_key)
        match = match_keys[0].match

        MatchPerformance.objects.filter(match=match).delete()

        if active_match_info["data"]["card"]["winner_team"] == "a":
            match.winning_team = match.team_one
        # match.winning_score = active_match_info["data"]["card"]["innings"]["a_1"]["runs"]
        elif active_match_info["data"]["card"]["winner_team"] == "b":
            match.winning_team = match.team_two

        if active_match_info["data"]["card"]["status_overview"] == "abandoned":
            match.match_result = Match.MR_ABANDONED
            match.save()
            print("Abandoned Match -- finishing")
            return

        elif active_match_info["data"]["card"]["msgs"]["result"] == "Match drawn":
            match.match_result = Match.MR_DRAW
        else:
            match.match_result = Match.MR_WIN

        match.match_status = Match.COMPLETED

        if (match.toss_decision == 2 and match.team_one == match.toss_winner) or (
            match.toss_decision == 1 and match.team_two == match.toss_winner
        ):
            first_innings = "b_1"
            second_innings = "a_1"
            match.bat_first_team = match.team_two
        else:
            first_innings = "a_1"
            second_innings = "b_1"
            match.bat_first_team = match.team_one

        self.update_innings_info(
            match, active_match_info, first_innings, "first_innings"
        )
        self.update_innings_info(
            match, active_match_info, second_innings, "second_innings"
        )

        if match.match_type == Match.TEST:
            self.update_innings_info(
                match,
                active_match_info,
                first_innings.replace("_1", "_2"),
                "third_innings",
            )
            self.update_innings_info(
                match,
                active_match_info,
                second_innings.replace("_1", "_2"),
                "fourth_innings",
            )

        match.save()

        for t in ("a", "b"):
            captain_key = active_match_info["data"]["card"]["teams"][t]["match"][
                "captain"
            ]
            wkeep_key = active_match_info["data"]["card"]["teams"][t]["match"]["keeper"]
            captain_player = Properties.objects.get(property_value=captain_key).player
            wkeep_player = Properties.objects.get(property_value=wkeep_key).player
            the_team = captain_player.team(match)
            self.update_match_performance(
                match, the_team, captain_player, "is_captain", True
            )
            self.update_match_performance(
                match, the_team, wkeep_player, "is_wicketkeeper", True
            )

        if active_match_info["data"]["card"]["man_of_match"]:
            man_of_match_key = active_match_info["data"]["card"]["man_of_match"]
            pth = PlayerTournamentHistory.objects.get(
                tournament=match.tournament,
                player__properties__property_value=man_of_match_key,
                player__properties__property_context="CricketAPI",
                player__properties__property_name="KEYS",
            )
            self.update_match_performance(
                match, pth.team, pth.player, "man_of_the_match", True
            )

        batting_stats = defaultdict(list)
        bowling_stats = defaultdict(list)
        for player in match.playing_eleven():
            # Batting Statistics: max 6, max 4, max runs
            stats = BattingPerformance.objects.filter(
                match=match, player=player
            ).aggregate(
                max_fours_hit=Sum("fours"),
                max_sixes_hit=Sum("sixes"),
                most_runs=Sum("runs"),
            )
            batting_stats[player] = stats

            # Bowling Statistics: max wickets
            stats = BowlingPerformance.objects.filter(
                match=match, player=player
            ).aggregate(most_wickets=Sum("wickets"))
            bowling_stats[player] = stats

        max_fours_hit_by = find_highest(batting_stats, "max_fours_hit")
        max_sixes_hit_by = find_highest(batting_stats, "max_sixes_hit")
        most_runs_hit_by = find_highest(batting_stats, "most_runs")
        most_wickets_by = find_highest(bowling_stats, "most_wickets")

        for p in max_fours_hit_by:
            self.update_match_performance(
                match, p.team(match), p, "max_fours_hit", True
            )
        for p in max_sixes_hit_by:
            self.update_match_performance(
                match, p.team(match), p, "max_sixes_hit", True
            )
        for p in most_runs_hit_by:
            self.update_match_performance(match, p.team(match), p, "most_runs", True)
        for p in most_wickets_by:
            self.update_match_performance(match, p.team(match), p, "most_wickets", True)

        # Last run and Last wicket of the winning team.
        if match.match_result == Match.MR_WIN:
            ballbyball_list = BallByBall.objects.filter(match=match).order_by(
                "-over", "-ball"
            )

            last_run_by = ballbyball_list.filter(
                batting_team=match.winning_team.team, runs__gt=0
            )[0].batsman

            last_wicket_by = (
                ballbyball_list.filter(bowling_team=match.winning_team.team)
                .filter(Q(wicket_type="catch") | Q(wicket_type="bowled"))[0]
                .bowler
            )

            self.update_match_performance(
                match, last_run_by.team(match), last_run_by, "last_run", True
            )

            self.update_match_performance(
                match, last_wicket_by.team(match), last_wicket_by, "last_wicket", True
            )

        # List of players who did not Bat.
        # for every team:
        for squad in (match.team_one, match.team_two):
            players = Player.objects.filter(squad__id=squad.id).exclude(
                battingperformance__match=match, battingperformance__team=squad.team
            )
            for player in players:
                bp = BattingPerformance()
                bp.player = player
                bp.match = match
                bp.team = squad.team
                bp.was_out = BattingPerformance.WO_DNB
                bp.comment = "Did Not Bat"
                bp.position = (
                    BattingPerformance.objects.filter(match=match)
                    .filter(team=squad.team)
                    .count()
                    + 1
                )

                bp.save()
