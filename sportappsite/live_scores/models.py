from django.db import models

from fixtures.models import Tournament, Team, Squad, Player, Match, PlayingSquad


class Properties(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.PROTECT, null=True, blank=True
    )
    match = models.ForeignKey(Match, on_delete=models.PROTECT, null=True, blank=True)
    squad = models.ForeignKey(Squad, on_delete=models.PROTECT, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, null=True, blank=True)
    player = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, blank=True)
    property_name = models.CharField(
        max_length=200, null=False, blank=False, default="KEYS"
    )
    property_value = models.CharField(max_length=200, null=False, blank=False)
    property_context = models.CharField(
        max_length=200, null=False, blank=False, default="CricketAPI"
    )

    @staticmethod
    def get_obj_cricketapi(key_value):
        return (
            Properties.objects.filter(property_value=key_value)
            .filter(property_context="CricketAPI")
            .filter(property_name="KEYS")
        )


class BallByBall(models.Model):
    batting_team = models.ForeignKey(
        Team, on_delete=models.PROTECT, null=True, related_name="batting_team"
    )
    bowling_team = models.ForeignKey(
        Team, on_delete=models.PROTECT, null=True, related_name="bowling_team"
    )
    match = models.ForeignKey(Match, on_delete=models.PROTECT, null=False)
    ball_key = models.CharField(max_length=50, null=False, default="abc")
    over = models.IntegerField(blank=False, null=False)
    ball = models.IntegerField(blank=False, null=False)
    batsman = models.ForeignKey(
        Player,
        null=False,
        on_delete=models.PROTECT,
        related_name="ball_by_ball_batsman",
    )
    bowler = models.ForeignKey(
        Player, null=False, on_delete=models.PROTECT, related_name="ball_by_ball_bowler"
    )
    wicket = models.ForeignKey(
        Player, null=True, on_delete=models.PROTECT, related_name="ball_by_ball_wicket"
    )
    # This will change to include more that 1 fielder recording in
    # case of runout/stumped.
    fielders = models.ForeignKey(
        Player, null=True, on_delete=models.PROTECT, related_name="ball_by_ball_fielder"
    )
    runs = models.IntegerField()
    extras = models.IntegerField()
    fours = models.BooleanField(default=False)
    sixes = models.BooleanField(default=False)
    dot_ball = models.BooleanField(default=False)
    # This shall have values like stumped, caughtby, runout, bowled
    wicket_type = models.CharField(max_length=50, null=True)
    ball_type = models.CharField(max_length=100, null=False, default="normal")
    last_ball_of_over = models.BooleanField(default=False)
    comments = models.CharField(max_length=10000, null=True)
    innings = models.IntegerField(default=1, null=False, blank=False)
