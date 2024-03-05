from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from django.contrib.auth.models import User

from members.models import (
    GroupLeaderBoard,
    LeaderBoardEntry,
    Member,
    MemberGroup,
    Membership,
)
from sportappsite import features

from members.utils import member_memberships, resolve_member

from predictions.models import (
    MemberPrediction,
    GroupSubmissionsConfig,
    SubmissionFieldConfig,
    MemberSubmission,
    MemberSubmissionData,
    PredictionScores,
    LeaderBoardScores,
    TouramentPredictionScore,
    MemberTournamentPrediction,
)

from fixtures.models import Match, Player, Team, Tournament, Country

from stats.models import PlayerScores, PlayerStat

from rules.models import (
    GroupPredictionScoringResult,
    GroupPostMatchPredictionScoringMethodResult,
    GroupLeaderBoardScoringMethodResult,
)

from configurations.models import MatchSubmissionNotes

from DynamicContent.models import MessageBlock

from app_media.models import AppMedia

from rewards.models import TournamentReward, TournamentRewardParticipant

POST_TOSS_NOTES = """
Toss for this Match is now done; you can make restricted changes to your
Prediction before the game starts.

You can:
==========

1. Change Super Player to any Player from your original, pre-toss selection.

2. If Players from your original selection are not in playing XI, they will
not show in the form and you can select a new Player in their place.

*****     In this case, NO MORE than 1 change is allowed.  *****
"""


# TODO cache
def match_specific_notes(match):
    try:
        match_note = MatchSubmissionNotes.objects.get(
            tournament=match.tournament, matches__in=(match,)
        )
    except MatchSubmissionNotes.DoesNotExist:
        return None
    else:
        return match_note.value


class AppMediaSerializer(serializers.ModelSerializer):
    media_file = serializers.SerializerMethodField()

    class Meta:
        model = AppMedia
        fields = ("media_name", "media_note", "media_size", "media_type", "media_file")

    def get_media_file(self, obj):
        return obj.media_file.url


class TournamentSerializer(serializers.ModelSerializer):
    media = AppMediaSerializer(many=True)

    class Meta:
        model = Tournament
        fields = (
            "id",
            "name",
            "abbreviation",
            "start_date",
            "tournament_level",
            "media",
            "submission_status",
        )


class TournamentWithAbbrevNameSerializer(serializers.ModelSerializer):
    media = AppMediaSerializer(many=True)
    name = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = (
            "id",
            "name",
            "abbreviation",
            "start_date",
            "tournament_level",
            "media",
            "submission_status",
        )

    def name(self, obj):
        return obj.abbreviation


class TeamSerializer(serializers.ModelSerializer):
    media = AppMediaSerializer(many=True)

    class Meta:
        model = Team
        fields = ("name", "abbreviation", "id", "media")


class MatchSerializer(serializers.ModelSerializer):
    venue = serializers.StringRelatedField()
    teams = TeamSerializer(many=True)
    submissions = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = (
            "teams",
            "submissions",
            "name",
            "id",
            "short_display_name",
            "venue",
            "local_start_time",
            "start_time_utc",
            "toss_time",
            "match_number",
            "match_type",
            "submission_status",
        )

    def get_submissions(self, obj):
        return int(MemberSubmission.objects.filter(match=obj).count())


class LeaderboardMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ("name", "id", "short_display_name")


class PlayerSerializer(serializers.ModelSerializer):
    media = AppMediaSerializer(many=True)

    class Meta:
        model = Player
        fields = ("name", "id", "media")


class MemberGroupNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberGroup
        fields = ("id", "name")


class MemberSerializer(serializers.ModelSerializer):
    avatar = AppMediaSerializer(many=True)

    class Meta:
        model = Member
        fields = ("name", "id", "avatar")


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ("id", "member_id", "is_admin")


class MemberGroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    admin_members = serializers.SerializerMethodField()
    rewards_enabled = serializers.SerializerMethodField()

    class Meta:
        model = MemberGroup
        fields = (
            "id",
            "name",
            "members",
            "invitation_code",
            "admin_members",
            "rewards_enabled",
        )

    def get_admin_members(self, obj):
        return [
            m.member_id
            for m in Membership.objects.filter(member_group=obj, is_admin=True)
        ]

    def get_rewards_enabled(self, obj):
        return features.group_rewards_enabled(obj)

    def get_members(self, obj):
        ms = obj.members.filter(membership__active=True)
        return MemberSerializer(ms, many=True).data


class MemberGroupOnlySerializer(serializers.ModelSerializer):
    admin_members = serializers.SerializerMethodField()

    class Meta:
        model = MemberGroup
        fields = (
            "id",
            "name",
            "invitation_code",
            "admin_members",
        )

    def get_admin_members(self, obj):
        return [
            m.member_id
            for m in Membership.objects.filter(member_group=obj, is_admin=True)
        ]


class LeaderBoardEntrySerializer(serializers.ModelSerializer):
    member = MemberSerializer()

    class Meta:
        model = LeaderBoardEntry
        exclude = ("leader_board",)


class GroupLeaderBoardSerializer(serializers.ModelSerializer):
    entries = LeaderBoardEntrySerializer(many=True, read_only=True)
    match = LeaderboardMatchSerializer()
    member_group = MemberGroupSerializer()
    tournament = TournamentWithAbbrevNameSerializer()
    available_leaderboards = serializers.SerializerMethodField()

    class Meta:
        model = GroupLeaderBoard
        fields = (
            "id",
            "computed_on",
            "board_number",
            "member_group",
            "match",
            "entries",
            "tournament",
            "available_leaderboards",
            "format",
            "is_tournament_leaderboard",
        )

    def get_available_leaderboards(self, obj):
        inactive = False

        if self.context["request"].query_params.get("tournament_active") != "True":
            inactive = True

        _, memberships = member_memberships(self.context["request"].user, inactive)
        return obj.available_leaderboards(memberships)


class PlayerScoreSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    team = TeamSerializer()
    match = MatchSerializer()

    class Meta:
        model = PlayerScores
        fields = ("player", "team", "match", "total_score")


class PredictionScoringResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPredictionScoringResult
        fields = ("rule_name", "result")


class PredictionScoresSerializer(serializers.ModelSerializer):
    detailed_scoring = serializers.ListSerializer(
        child=PredictionScoringResultSerializer()
    )

    class Meta:
        model = PredictionScores
        fields = ("detailed_scoring",)


class PostPredictionScoringResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPostMatchPredictionScoringMethodResult
        fields = ("rule_name", "result")


class LeaderBoardScoringResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupLeaderBoardScoringMethodResult
        fields = ("rule_name", "result")


class PostPredictionScoresSerializer(serializers.ModelSerializer):
    detailed_scoring = serializers.ListSerializer(
        child=PostPredictionScoringResultSerializer()
    )

    class Meta:
        model = PredictionScores
        fields = ("detailed_scoring",)


class LeaderBoardScoresSerializer(serializers.ModelSerializer):
    detailed_scoring = serializers.ListSerializer(
        child=LeaderBoardScoringResultSerializer()
    )

    class Meta:
        model = LeaderBoardScores
        fields = ("detailed_scoring",)


class MemberSubmissionDataSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    team = TeamSerializer()
    field = serializers.CharField()

    class Meta:
        model = MemberSubmissionData
        fields = ("field_name", "team", "player", "value", "field")


class MemberSubmissionSerializer(serializers.ModelSerializer):
    submission_data = MemberSubmissionDataSerializer(many=True, read_only=True)
    submission_time = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    member = MemberSerializer()

    class Meta:
        model = MemberSubmission
        fields = (
            "member",
            "submission_time",
            "submission_data",
        )


class MemberSubmissionWithColumnOrderingSerializer(serializers.Serializer):
    table_column_ordering = serializers.ListSerializer(child=serializers.CharField())
    data = MemberSubmissionSerializer(many=True)


class MemberPredictionScoreSerializer(serializers.ModelSerializer):
    member = MemberSerializer()
    match = MatchSerializer()
    member_group = MemberGroupNameSerializer()
    player_scores = serializers.ListSerializer(child=PlayerScoreSerializer())
    prediction_scores = PredictionScoresSerializer()
    post_prediction_scores = PostPredictionScoresSerializer()
    leaderboard_scores = LeaderBoardScoresSerializer()
    player_one = PlayerSerializer()
    player_two = PlayerSerializer()
    player_three = PlayerSerializer()
    super_player = PlayerSerializer()
    predicted_winning_team = TeamSerializer()

    class Meta:
        model = MemberPrediction
        fields = (
            "member",
            "match",
            "member_group",
            "total_prediction_score",
            "player_scores",
            "prediction_scores",
            "post_prediction_scores",
            "leaderboard_scores",
            "player_one",
            "player_two",
            "player_three",
            "super_player",
            "predicted_winning_team",
            "predicted_winning_team_score",
            "total_wickets",
            "total_fours",
            "total_sixes",
            "total_prediction_score",
            "first_innings_run_lead",
        )


class MemberPredictionScoreWithColumnOrderingSerializer(serializers.Serializer):
    table_column_ordering = serializers.ListSerializer(child=serializers.CharField())
    data = MemberPredictionScoreSerializer(many=True)


class MemberPredictionSerializer(serializers.ModelSerializer):
    member = MemberSerializer()
    member_group = MemberGroupNameSerializer()
    match = MatchSerializer()
    table_display_name = serializers.SerializerMethodField()
    player_one = PlayerSerializer()
    player_two = PlayerSerializer()
    player_three = PlayerSerializer()
    super_player = PlayerSerializer()
    predicted_winning_team = TeamSerializer()

    # TODO -- fields should be dynamically calculated based on table_column_ordering,
    #         which is essentially what needs to be shown as per config.
    class Meta:
        model = MemberPrediction
        fields = (
            "member",
            "match",
            "table_display_name",
            "member_group",
            "player_one",
            "player_two",
            "player_three",
            "super_player",
            "predicted_winning_team",
            "predicted_winning_team_score",
            "total_wickets",
            "total_fours",
            "total_sixes",
            "total_prediction_score",
            "first_innings_run_lead",
        )

    def get_table_display_name(self, obj):
        return obj.match.name.replace(obj.match.tournament.name + ", ", "")


class MemberPredictionWithColumnOrderingSerializer(serializers.Serializer):
    table_column_ordering = serializers.ListSerializer(child=serializers.CharField())
    data = MemberPredictionSerializer(many=True)


class RegisterMemberSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    first_name = serializers.CharField(
        max_length=30, required=True, allow_blank=False, min_length=2
    )
    last_name = serializers.CharField(
        max_length=30, required=True, allow_blank=False, min_length=2
    )
    password = serializers.CharField(
        max_length=30, required=True, allow_blank=False, min_length=10
    )
    invitation_code = serializers.CharField(
        max_length=8, required=False, allow_blank=False
    )


class RegisterMemberGroupSerializer(serializers.Serializer):
    member_group_name = serializers.CharField(
        max_length=50, min_length=3, required=True, allow_blank=False
    )


class SubmitMatchPredictionSerializer(serializers.Serializer):
    match = serializers.IntegerField(required=True, min_value=1)
    member_group = serializers.IntegerField(required=True, min_value=1)
    tournament = serializers.IntegerField(required=True, min_value=1)
    submission_data = serializers.DictField(
        required=True, child=serializers.CharField()
    )
    crosspost = serializers.BooleanField(required=True)


class SubmitTournamentPredictionSerializer(serializers.Serializer):
    member_group = serializers.IntegerField(required=True, min_value=1)
    tournament = serializers.IntegerField(required=True, min_value=1)
    tournament_format = serializers.IntegerField(required=True)
    submission_data = serializers.DictField(
        required=True, child=serializers.CharField()
    )
    crosspost = serializers.BooleanField(required=True)


class SubmissionFieldSeralizer(serializers.ModelSerializer):
    range_data = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()

    class Meta:
        model = SubmissionFieldConfig
        fields = (
            "form_order",
            "description",
            "field_model",
            "field",
            "is_compulsory",
            "form_category",
            "is_enabled",
            "range_data",
            "is_reactive",
            "reactions",
        )

    def get_range_data(self, obj):
        return obj.build_range_data(match=None)

    def get_reactions(self, obj):
        return obj.build_reactions(match=None)


class GroupMatchSubmissionsConfigSerializer(serializers.ModelSerializer):
    tournament = TournamentSerializer()
    member_group = MemberGroupNameSerializer()
    match_submission_data = serializers.SerializerMethodField()
    submission_notes = serializers.SerializerMethodField()

    class Meta:
        model = GroupSubmissionsConfig
        fields = (
            "member_group",
            "tournament",
            "submission_notes",
            "match_submission_data",
        )

    def get_submission_notes(self, obj):
        match_id = self.context["request"].query_params.get("match")
        match = Match.objects.get(id=match_id)
        specific_notes = match_specific_notes(match)

        if match.post_toss_changes_allowed:
            return POST_TOSS_NOTES
        elif specific_notes:
            return specific_notes
        else:
            return obj.submission_notes

    def get_match_submission_data(self, obj):
        match_id = self.context["request"].query_params.get("match")
        member = resolve_member(self.context["request"].user)
        return obj.allowed_match_submission_data(match_id, member)


class GroupTournamentSubmissionsConfigDetailsSerializer(serializers.ModelSerializer):
    submission_fields = SubmissionFieldSeralizer(many=True)
    allowed_tournament_submission_data = serializers.DictField()

    class Meta:
        model = GroupSubmissionsConfig
        fields = (
            "submission_notes",
            "submission_fields",
            "allowed_tournament_submission_data",
        )


class GroupTournamentSubmissionsConfigSerializer(serializers.ModelSerializer):
    tournament = TournamentSerializer()
    member_group = MemberGroupNameSerializer()

    class Meta:
        model = GroupSubmissionsConfig
        fields = (
            "member_group",
            "tournament",
            "tournament_format",
            "active_from",
            "active_to",
        )


class InvitedMemberSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=2, max_length=30, required=True)
    email = serializers.EmailField(required=True)


class MemberGroupInvitations(serializers.Serializer):
    invites = serializers.ListField(
        child=InvitedMemberSerializer(), required=True, min_length=1, max_length=5
    )
    member_group = serializers.IntegerField(min_value=1, required=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=30, required=True, allow_blank=False, min_length=10
    )
    new_password = serializers.CharField(
        max_length=30,
        required=True,
        allow_blank=False,
        min_length=10,
        error_messages={"min_length": "Please enter 10 or more characters."},
    )

    def validate_new_password(self, value):
        validate_password(value)
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)


class TouramentPredictionScoreSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()
    teams = serializers.SerializerMethodField()
    player = serializers.SerializerMethodField()
    rule = serializers.CharField()
    points = serializers.IntegerField()

    class Meta:
        model = TouramentPredictionScore
        fields = ("member", "teams", "player", "rule", "points")

    def get_member(self, obj):
        return obj.prediction.member.name()

    def get_teams(self, obj):
        t = None
        if obj.team_one:
            t = obj.team_one.name
        if obj.team_two:
            t = t + ", {}".format(obj.team_two.name)
        if obj.team_three:
            t = t + ", {}".format(obj.team_three.name)
        if obj.team_four:
            t = t + ", {}".format(obj.team_four.name)

        return t

    def get_player(self, obj):
        if obj.player:
            return obj.player.name


class MemberTouramentPredictionSerializer(serializers.ModelSerializer):
    prediction_scores = serializers.SerializerMethodField()
    tournament = TournamentSerializer()
    member = MemberSerializer()
    member_group = MemberGroupNameSerializer()
    tournament_winning_team = TeamSerializer()
    runner_up = TeamSerializer()
    top_team_one = TeamSerializer()
    top_team_two = TeamSerializer()
    top_team_three = TeamSerializer()
    top_team_four = TeamSerializer()
    last_team = TeamSerializer()
    top_batsman_one = PlayerSerializer()
    top_batsman_two = PlayerSerializer()
    top_batsman_three = PlayerSerializer()
    top_bowler_one = PlayerSerializer()
    top_bowler_two = PlayerSerializer()
    top_bowler_three = PlayerSerializer()
    most_valuable_player_one = PlayerSerializer()
    most_valuable_player_two = PlayerSerializer()
    most_valuable_player_three = PlayerSerializer()
    player_of_the_tournament_one = PlayerSerializer()
    player_of_the_tournament_two = PlayerSerializer()

    class Meta:
        model = MemberTournamentPrediction
        fields = (
            "member",
            "tournament",
            "member_group",
            "prediction_scores",
            "prediction_format",
            "tournament_winning_team",
            "runner_up",
            "top_team_one",
            "top_team_two",
            "top_team_three",
            "top_team_four",
            "last_team",
            "top_batsman_one",
            "top_batsman_two",
            "top_batsman_three",
            "top_bowler_one",
            "top_bowler_two",
            "top_bowler_three",
            "most_valuable_player_one",
            "most_valuable_player_two",
            "most_valuable_player_three",
            "win_series_margin",
            "player_of_the_tournament_one",
            "player_of_the_tournament_two",
        )

    def get_prediction_scores(self, obj):
        prediction_scores = TouramentPredictionScore.objects.filter(prediction=obj)

        prediction_scores_serializer = TouramentPredictionScoreSerializer(
            prediction_scores, many=True
        )

        return prediction_scores_serializer.data


class MemberTouramentPredictionWithColumnOrderingSerializer(serializers.Serializer):
    table_column_ordering = serializers.ListSerializer(child=serializers.CharField())
    data = MemberTouramentPredictionSerializer(many=True)


class PlayerStatSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    team = TeamSerializer()
    tournament_total = serializers.SerializerMethodField()
    tournament = TournamentSerializer()

    class Meta:
        model = PlayerStat
        fields = ("player", "team", "tournament_total", "tournament")

    def get_tournament_total(self, obj):
        return int(obj.stat_value)


class ContactFormSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=20, required=True)
    email = serializers.EmailField(required=True)
    mobile_number = serializers.CharField(max_length=20, required=True)
    message = serializers.CharField(max_length=500, required=True)


class MessageBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageBlock
        fields = (
            "id",
            "message_name",
            "content_block",
            "tournament",
            "member",
            "member_group",
            "notes",
        )


class JoinMemberGroupSerializer(serializers.Serializer):
    invitation_code = serializers.CharField(max_length=8, required=True)


class TournamentRewardParticipantSerializer(serializers.ModelSerializer):
    member = MemberSerializer()

    class Meta:
        model = TournamentRewardParticipant
        fields = (
            "id",
            "member",
            "contributor",
            "contribution_amount",
            "contribution_received",
        )


class SubmitTournamentRewardParticipantSerializer(serializers.DictField):
    class Meta:
        fields = ("participant_id", "contributor", "contribution_amount")


class TournamentRewardSerializer(serializers.ModelSerializer):
    tournament = TournamentSerializer()
    member_group = MemberGroupSerializer()
    locked = serializers.SerializerMethodField()
    participants = TournamentRewardParticipantSerializer(many=True)

    class Meta:
        model = TournamentReward
        fields = (
            "id",
            "tournament",
            "member_group",
            "reward_pool",
            "contribution_per_member",
            "activated",
            "locked",
            "participants",
            "agreement_text",
            "rewards_calculations_text",
            "tournament_format",
            "changes_allowed_up_to",
            "changes_allowed_up_to_utc",
        )

    def get_locked(self, obj):
        member = resolve_member(self.context["request"].user)
        is_admin = Membership.objects.get(
            member=member, member_group=obj.member_group
        ).is_admin

        if not is_admin:
            return True

        if is_admin:
            if obj.activated:
                return True
            else:
                return False


class SubmitTournamentRewardSerializer(serializers.Serializer):
    tournament_reward = serializers.IntegerField(required=True, min_value=1)
    reward_pool = serializers.IntegerField(required=True, min_value=1)
    contribution_per_member = serializers.IntegerField(required=True, min_value=0)
    participants = serializers.ListField(
        required=True, child=SubmitTournamentRewardParticipantSerializer()
    )


class PredictionStatSerializer(serializers.Serializer):
    stat_name = serializers.CharField(max_length=20, required=True)
    stat_value = serializers.CharField(max_length=20, required=True)
    stat_unit = serializers.CharField(max_length=20, required=True)
    stat_index = serializers.IntegerField()
    member_group = MemberGroupNameSerializer()
    team_id = serializers.IntegerField()


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            "id",
            "name",
            "code",
            "calling_code",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "username",
        )
        extra_kwargs = {
            "first_name": {"required": True, "allow_null": False, "allow_blank": False},
            "last_name": {"required": True, "allow_null": False, "allow_blank": False},
            "username": {"required": False, "allow_null": False, "allow_blank": False},
            "email": {"required": False, "allow_null": False, "allow_blank": False},
        }


class MemberProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    avatar = AppMediaSerializer(many=True, required=False)

    class Meta:
        model = Member
        fields = (
            "nick_name",
            "country",
            "date_of_birth",
            "gender",
            "user",
            "avatar",
        )
        extra_kwargs = {
            "nick_name": {"required": True, "allow_null": False, "allow_blank": False},
            "country": {"required": True, "allow_null": False},
            "date_of_birth": {"required": True, "allow_null": False},
            "gender": {"required": True, "allow_null": False, "allow_blank": False},
        }
