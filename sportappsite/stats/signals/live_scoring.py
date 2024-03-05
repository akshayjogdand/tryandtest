from django.db.models.signals import post_save
from django.dispatch import receiver
from live_scores.models import BallByBall
from stats.models import BattingPerformance, BowlingPerformance, FieldingPerformance


@receiver(post_save, sender=BallByBall)
def update_performances(sender, instance, **kwargs):

    # Batsman performance object instantiation
    batsman_performance = BattingPerformance()
    batsman_records = BattingPerformance.objects.filter(
        player=instance.batsman,
        match=instance.match,
        team=instance.batting_team,
        innings=instance.innings,
    )
    if batsman_records:
        batsman_performance = batsman_records[0]
    else:
        batsman_performance.player = instance.batsman
        batsman_performance.match = instance.match
        batsman_performance.innings = instance.innings
        batsman_performance.team = instance.batting_team
        batsman_performance.was_out = BattingPerformance.WO_NOT_OUT
        batsman_performance.position = (
            BattingPerformance.objects.filter(
                match=instance.match,
                innings=instance.innings,
                team=instance.batting_team,
            ).count()
            + 1
        )

    # Batsman runs
    batsman_performance.runs += instance.runs
    if instance.ball_type != "wide":
        batsman_performance.balls += 1
    if instance.dot_ball:
        batsman_performance.zeros += 1
    else:
        if instance.fours:
            batsman_performance.fours += 1
        elif instance.sixes:
            batsman_performance.sixes += 1
        elif instance.runs == 1:
            batsman_performance.ones += 1
        elif instance.runs == 2:
            batsman_performance.twos += 1
        elif instance.runs == 3:
            batsman_performance.threes += 1
        elif instance.runs == 5:
            batsman_performance.fives += 1
        elif instance.runs == 7:
            batsman_performance.seven_plus += 1

    # Batsman wicket details
    if instance.wicket_type:
        if instance.wicket != batsman_performance.player:

            wicket_performance = BattingPerformance()
            wicket_records = BattingPerformance.objects.filter(
                player=instance.wicket,
                match=instance.match,
                team=instance.batting_team,
                innings=instance.innings,
            )
            if wicket_records:
                wicket_performance = wicket_records[0]
            else:
                wicket_performance.player = instance.wicket
                wicket_performance.match = instance.match
                wicket_performance.innings = instance.innings
                wicket_performance.team = instance.batting_team
                wicket_performance.position = (
                    BattingPerformance.objects.filter(
                        match=instance.match,
                        team=instance.batting_team,
                        innings=instance.innings,
                    ).count()
                    + 1
                )

            if instance.wicket_type == "retirehut":
                wicket_performance.was_out = BattingPerformance.WO_NOT_OUT
                wicket_performance.dismissal = BattingPerformance.RETIRED_HURT
            elif instance.wicket_type == "runout":
                wicket_performance.was_out = BattingPerformance.WO_OUT
                wicket_performance.dismissal = BattingPerformance.RUN_OUT
                wicket_performance.save()
                if instance.fielders:
                    wicket_performance.fielder.add(instance.fielders)
                wicket_performance.bowler = instance.bowler

            wicket_performance.save()

        else:
            if instance.wicket_type == "retirehut":
                wicket_performance.was_out = BattingPerformance.WO_NOT_OUT
                wicket_performance.dismissal = BattingPerformance.RETIRED_HURT
            else:
                batsman_performance.was_out = BattingPerformance.WO_OUT
                if instance.wicket_type == "catch":
                    batsman_performance.dismissal = BattingPerformance.CAUGHT
                elif instance.wicket_type == "bowled":
                    batsman_performance.dismissal = BattingPerformance.BOWLED
                elif instance.wicket_type == "runout":
                    batsman_performance.dismissal = BattingPerformance.RUN_OUT
                elif (
                    instance.wicket_type == "stumbed"
                    or instance.wicket_type == "stumped"
                ):
                    batsman_performance.dismissal = BattingPerformance.STUMPED
                batsman_performance.save()
                # Fielder details
                if instance.fielders:
                    batsman_performance.fielder.add(instance.fielders)
                batsman_performance.bowler = instance.bowler

    batsman_performance.save()

    # Bowler Performance
    bowler_performance = BowlingPerformance()
    bowler_records = BowlingPerformance.objects.filter(
        player=instance.bowler,
        match=instance.match,
        innings=instance.innings,
        team=instance.bowling_team,
    )
    if bowler_records:
        bowler_performance = bowler_records[0]
    else:
        bowler_performance.player = instance.bowler
        bowler_performance.match = instance.match
        bowler_performance.innings = instance.innings
        bowler_performance.team = instance.bowling_team

    # Bowler runs
    bowler_performance.extras += instance.extras
    bowler_performance.runs += instance.runs
    if (
        instance.ball_type == "normal"
        or instance.ball_type == "legbye"
        or instance.ball_type == "bye"
    ):
        bowler_performance.balls += 1
    if instance.fours:
        bowler_performance.fours += 1
    if instance.sixes:
        bowler_performance.sixes += 1

    # Dotball & Maiden over calculation
    if instance.dot_ball:
        bowler_performance.dot_balls += 1
        # Maiden Over
        if instance.ball == 1:
            bowler_performance.is_maiden = True
        elif instance.last_ball_of_over and bowler_performance.is_maiden:
            bowler_performance.maiden += 1
            bowler_performance.is_maiden = False
    else:
        bowler_performance.is_maiden = False

    if instance.last_ball_of_over:
        if bowler_performance.balls >= 6:
            bowler_performance.overs += 1
            bowler_performance.balls = 0

    # hattrick calculation
    if instance.wicket_type:
        bowler_performance.wickets += 1
        if bowler_performance.hattrick_count + 1 == 3:
            bowler_performance.hat_tricks += 1
            bowler_performance.hattrick_count = 0
        else:
            bowler_performance.hattrick_count += 1
    else:
        bowler_performance.hattrick_count = 0

    bowler_performance.save()

    # Fielder performance
    if instance.fielders:
        # for fielder in instance.fielders:
        # this logic shall be in above for loop when multiple fielder information is available.
        fielder = instance.fielders
        fielder_performance = FieldingPerformance()
        fielder_records = FieldingPerformance.objects.filter(
            player=fielder,
            match=instance.match,
            innings=instance.innings,
            team=instance.bowling_team,
        )
        if fielder_records:
            fielder_performance = fielder_records[0]
        else:
            fielder_performance.player = fielder
            fielder_performance.match = instance.match
            fielder_performance.innings = instance.innings
            fielder_performance.team = instance.bowling_team

        if instance.wicket_type == "catch":
            fielder_performance.catches += 1
        elif instance.wicket_type == "runout":
            fielder_performance.runouts += 1
        elif instance.wicket_type == "stmped" or instance.wicket_type == "stumbed":
            fielder_performance.stumpings += 1
        else:
            print(instance.wicket_type)

        fielder_performance.save()
