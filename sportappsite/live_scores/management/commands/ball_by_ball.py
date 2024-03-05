import time
import logging

import pycricket

from django.core.management.base import BaseCommand

from fixtures.models import (
    Player,
    Match,
)

from live_scores.models import Properties, BallByBall

from stats.models import BattingPerformance, BowlingPerformance, FieldingPerformance


class Command(BaseCommand):

    logger = logging.getLogger("live_scores.ball_by_ball")

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("match_key", nargs="+", type=str)
        parser.add_argument(
            "--over_interval",
            "-interval",
            type=int,
            default=300,
            help="time interval between querying two overs",
        )
        parser.add_argument(
            "--redo",
            "-r",
            action="store_true",
            help="deletes existing information about the match and "
            "re-records the live scoring",
        )
        parser.add_argument(
            "--team",
            "-t",
            type=str,
            choices=["a", "b"],
            help="provide the team for which you need live scoring. "
            "The team should be provided as 'a' or 'b'",
        )
        parser.add_argument(
            "--innings",
            "-i",
            type=int,
            choices=[1, 2],
            default=1,
            help="Innings to fetch and record data for.",
        )

        parser.add_argument(
            "--start_over",
            "-start",
            type=int,
            default=1,
            help="start over for which the live scoring has to be done",
        )
        parser.add_argument(
            "--end_over",
            "-end",
            type=int,
            default=20,
            help="end over till which the live scoring has to be done",
        )

    def addPlayer(self, player_key, player_name, start):

        player = Player()
        if player_name is None:
            player_stats = start.get_player_stats(player_key, "ipl")

            if player_stats["status_code"] == 200:
                player_list = Player.objects.filter(
                    name=player_stats["data"]["player"]["name"]
                )
                # This Condition should not come
                if not player_list:
                    player.name = player_stats["data"]["player"]["name"]
                    player.save()
                else:
                    player = player_list[0]

            else:
                # call the Error function and continue
                player.name = player_key
                player.save()
        else:
            player.name = player_name
            player.save()

        player_key_obj = Properties()
        player_key_obj.player = player
        player_key_obj.property_value = player_key
        player_key_obj.save()

        return player

    # returns information for over_complete

    def error_handling(self, start, match_key, over_interval, over, max_overs):

        try:
            active_match_info = start.get_match(match_key)
            if active_match_info:
                match_status = active_match_info["data"]["card"]["status_overview"]
                if (
                    (match_status == "abandoned")
                    or (match_status == "canceled")
                    or (match_status == "result")
                ):

                    if over == max_overs:
                        return True, over

                    else:
                        return False, over + 1

                elif match_status != "in_play":
                    self.logger.info("Long interval as the status is: %s", match_status)
                    time.sleep(over_interval)

                    return False, over

        except:
            self.logger.error("Error: accessing match info match_key - %s", match_key)

            return True, over

    def handle(self, *args, **options):

        handler = pycricket.RcaStorageHandler()
        start = pycricket.RcaApp(
            access_key="eed6178168b033260de5884da95eebb5",
            secret_key="0d1cda0c712d0b861841765a9c5673d4",
            app_id="2208",
            store_handler=handler,
        )

        # Get match details
        match_key = options["match_key"][0]
        match_list = Properties.get_obj_cricketapi(match_key)
        match = match_list[0].match

        innings = str(options["innings"])

        if options["over_interval"]:
            over_interval = options["over_interval"]

        if options["start_over"]:
            start_over = options["start_over"]

        if options["end_over"]:
            end_over = options["end_over"]

        if options["team"]:
            teams = options["team"]
        else:
            # get information about the toss
            if (
                match.toss_decision == 2
                and match.team_one.team == match.toss_winner.team
            ) or (
                match.toss_decision == 1
                and match.team_two.team == match.toss_winner.team
            ):
                teams = ["b", "a"]
            else:
                teams = ["a", "b"]

        if options["redo"]:
            BallByBall.objects.filter(match=match, innings=innings).delete()
            BattingPerformance.objects.filter(match=match, innings=innings).delete()
            BowlingPerformance.objects.filter(match=match, innings=innings).delete()
            FieldingPerformance.objects.filter(match=match, innings=innings).delete()
            match.winning_team = None
            match.match_result = Match.MR_UNKNOWN
            match.match_status = Match.LIVE

        for team in teams:
            over_complete = False
            over = start_over
            max_overs = end_over
            over_querying_count = 3
            sleep_time = over_interval
            # sleep_time = 0.5

            if team == "b":
                batting_team = match.team_two.team
                bowling_team = match.team_one.team
            if team == "a":
                batting_team = match.team_one.team
                bowling_team = match.team_two.team

            # check match_status. Only if match_status is in_play or result start the loop.
            try:
                active_match_info = start.get_match(match_key)
                if active_match_info:
                    match_status = active_match_info["data"]["card"]["status_overview"]
                    self.logger.info("Match Status %s", match_status)

                    while (
                        (match_status != "in_play")
                        and (match_status != "result")
                        and (match_status != "abandoned")
                    ):
                        time.sleep(300)
                        active_match_info = start.get_match(match_key)
                        if active_match_info:
                            match_status = active_match_info["data"]["card"][
                                "status_overview"
                            ]

                    while not over_complete:

                        over_key = team + "_" + innings + "_" + str(over)
                        time.sleep(over_interval)
                        self.logger.info("Over interval time %d", over_interval)

                        try:
                            over_info = start.get_ball_by_ball(
                                match_key, over_key=over_key
                            )
                            over_querying_count -= 1

                            if over_info["status_code"] == 200:

                                self.logger.info("Over_key: %s", over_key)
                                balls = over_info["data"]["over"]["balls"]
                                ball_count = 1
                                normal_balls = 0

                                for ball in balls:

                                    ball_details_list = (
                                        BallByBall.objects.filter(match=match)
                                        .filter(batting_team=batting_team)
                                        .filter(over=over - 1)
                                        .filter(ball_key=ball)
                                    )

                                    # ball_details not available then persist it
                                    if not ball_details_list:
                                        ball_details = BallByBall()

                                        # match and team
                                        ball_details.match = match
                                        ball_details.batting_team = batting_team
                                        ball_details.bowling_team = bowling_team
                                        ball_details.ball_key = ball
                                        ball_details.innings = innings

                                        # batsman
                                        batsman_keys = Properties.get_obj_cricketapi(
                                            over_info["data"]["balls"][ball]["batsman"][
                                                "key"
                                            ]
                                        )
                                        if not batsman_keys:
                                            ball_details.batsman = self.addPlayer(
                                                over_info["data"]["balls"][ball][
                                                    "batsman"
                                                ]["key"],
                                                None,
                                                start,
                                            )
                                        else:
                                            ball_details.batsman = batsman_keys[
                                                0
                                            ].player

                                        # bowler
                                        bowler_keys = Properties.get_obj_cricketapi(
                                            over_info["data"]["balls"][ball]["bowler"][
                                                "key"
                                            ]
                                        )
                                        if not bowler_keys:
                                            ball_details.bowler = self.addPlayer(
                                                over_info["data"]["balls"][ball][
                                                    "bowler"
                                                ]["key"],
                                                None,
                                                start,
                                            )
                                        else:
                                            ball_details.bowler = bowler_keys[0].player

                                        # Score details
                                        ball_details.ball_type = over_info["data"][
                                            "balls"
                                        ][ball]["ball_type"]
                                        ball_details.runs = over_info["data"]["balls"][
                                            ball
                                        ]["batsman"]["runs"]
                                        if (
                                            over_info["data"]["balls"][ball]["batsman"][
                                                "four"
                                            ]
                                            == 1
                                        ):
                                            ball_details.fours = True
                                        if (
                                            over_info["data"]["balls"][ball]["batsman"][
                                                "six"
                                            ]
                                            == 1
                                        ):
                                            ball_details.sixes = True
                                        if (
                                            over_info["data"]["balls"][ball]["batsman"][
                                                "dotball"
                                            ]
                                            == 1
                                            or ball_details.ball_type == "bye"
                                            or ball_details.ball_type == "legbye"
                                        ):
                                            ball_details.dot_ball = True
                                        ball_details.extras = over_info["data"][
                                            "balls"
                                        ][ball]["bowler"]["extras"]

                                        # Wicket Details
                                        if over_info["data"]["balls"][ball]["wicket"]:
                                            wicket_keys = Properties.get_obj_cricketapi(
                                                over_info["data"]["balls"][ball][
                                                    "wicket"
                                                ]
                                            )
                                            if not wicket_keys:
                                                ball_details.wicket = self.addPlayer(
                                                    over_info["data"]["balls"][ball][
                                                        "wicket"
                                                    ],
                                                    None,
                                                    start,
                                                )
                                            else:
                                                ball_details.wicket = wicket_keys[
                                                    0
                                                ].player

                                            ball_details.wicket_type = over_info[
                                                "data"
                                            ]["balls"][ball]["wicket_type"]

                                            if over_info["data"]["balls"][ball][
                                                "fielder"
                                            ]:
                                                fielder_keys = Properties.get_obj_cricketapi(
                                                    over_info["data"]["balls"][ball][
                                                        "fielder"
                                                    ]["key"]
                                                )
                                                if not fielder_keys:
                                                    ball_details.fielders = self.addPlayer(
                                                        over_info["data"]["balls"][
                                                            ball
                                                        ]["fielder"]["key"],
                                                        None,
                                                        start,
                                                    )
                                                else:
                                                    ball_details.fielders = fielder_keys[
                                                        0
                                                    ].player

                                            ball_details.comments = over_info["data"][
                                                "balls"
                                            ][ball]["wicket_type"]

                                        # Over Details
                                        ball_details.over = over - 1
                                        ball_details.ball = over_info["data"]["balls"][
                                            ball
                                        ]["ball"]

                                    else:
                                        ball_details = ball_details_list[0]

                                    if (
                                        ball_details.ball_type == "normal"
                                        or ball_details.ball_type == "legbye"
                                        or ball_details.ball_type == "bye"
                                    ):
                                        normal_balls += 1

                                    if (
                                        (over_info["data"]["next_over"] is None)
                                        and (
                                            over_info["data"]["match"][
                                                "status_overview"
                                            ]
                                            == "result"
                                            or over_info["data"]["match"][
                                                "status_overview"
                                            ]
                                            == "innings_break"
                                            or over == max_overs
                                        )
                                    ) or (
                                        (over_info["data"]["next_over"] is not None)
                                        and (
                                            over_info["data"]["next_over"].split("_")[0]
                                            != over_info["data"]["over"]["team"]
                                        )
                                    ):

                                        if ball_count == len(balls):
                                            if not ball_details_list:
                                                ball_details.last_ball_of_over = True
                                            over_complete = True

                                    elif (
                                        normal_balls >= 6 and ball_count == len(balls)
                                    ) or (
                                        (ball_count == len(balls))
                                        and over_querying_count == 0
                                    ):

                                        if not ball_details_list:
                                            ball_details.last_ball_of_over = True
                                        over = over + 1
                                        over_querying_count = 3
                                        over_interval = sleep_time

                                    elif over_querying_count > 0 and ball_count == len(
                                        balls
                                    ):
                                        # Commented code seems to look for a delayed end to the over as
                                        # not all balls bowled. However if match is abandoned, this stalls.
                                        # Perhaps not needed at all as we are not querying live matches.

                                        pass

                                        # over_interval = abs((6 - normal_balls) * 50)
                                        # self.logger.info(
                                        # "setting over_interval to %d %d %d",
                                        # over_interval,
                                        # sleep_time,
                                        # over_querying_count,
                                        # )

                                    if not ball_details_list:
                                        ball_details.save()
                                    ball_count = ball_count + 1
                                    # end of for loop for balls

                            else:
                                self.logger.error(
                                    "Error: accessing over info over_key - %s "
                                    "error_code: %d",
                                    over_key,
                                    over_info["status_code"],
                                )

                                if over > max_overs:
                                    self.logger.error(
                                        "Finishing innings data fetch as over={} max_overs={}".format(
                                            over, max_overs
                                        )
                                    )
                                    over_complete = True

                                # Assume we still have more overs to fetch.
                                # Anything like adbandoned matches with 3ov 2balls played should be caught by above.
                                else:
                                    over_complete, over = self.error_handling(
                                        start, match_key, over_interval, over, max_overs
                                    )

                        except Exception as e:
                            self.logger.error(
                                "Error: accessing over info over_key - %s "
                                "with exception %s",
                                over_key,
                                e,
                            )
                            over_complete, over = self.error_handling(
                                start, match_key, over_interval, over, max_overs
                            )

            except Exception as e:
                self.logger.error(
                    "Error: accessing over info match_key - %s with exception %s",
                    match_key,
                    e,
                )
