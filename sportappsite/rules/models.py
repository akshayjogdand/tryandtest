from django.db import models

from django.core.exceptions import ValidationError

from reversion import revisions as reversion

from python_field.python_field import PythonCodeField

from python_field.utils import is_code_and_lambda


def apply_changes_to_clones(rule):
    SKIP_CLONING_FIELDS = ["notes", "id"]

    rule_klass = type(rule)
    if rule_klass not in DEFAULT_RULE_TYPES:
        return

    mapped_child_klass, _ = RULE_TO_MEMBER_GROUP_RULE_MAPPING.get(rule_klass)

    for cloned_rule in mapped_child_klass.objects.filter(parent_rule=rule).all():
        for fields in rule._meta.fields:
            attr_name = fields.attname
            if attr_name not in SKIP_CLONING_FIELDS:
                setattr(cloned_rule, attr_name, getattr(rule, attr_name))
        cloned_rule.save()


class Rule(models.Model):
    # When to apply Rule
    NOT_SET = -1
    PLAYER_SCORING = 0
    MEMBER_PREDICTION_VALIDATION = 1
    MEMBER_PREDICTION_SCORING = 2
    POST_MATCH_PREDICTION_SCORING = 3
    LEADERBOARD_SCORING = 4
    TOURNAMENT_SCORING = 5

    MATCH_NUMBER_CHECK_LAMBDA_STR = "lambda match: True"

    DO_NOT_APPLY_CHANGES_TO_CLONES = False
    APPLY_CHANGES_TO_CLONES = True

    # Rule Categories
    CAT_NOT_SET = -1
    BATTING_CATEGORY = 0
    BOWLING_CATEGORY = 1
    FIELDING_CATEGORY = 2
    GENERAL_CATEGORY = 3
    TEAM_CATEGORY = 4

    # Display Types
    DISPLAY_POINTS = 0
    DISPLAY_FACTOR = 1
    DISPLAY_RANGES = 2

    # Match Types
    ONE_DAY = 1
    T_TWENTY = 2
    TEST = 3

    _default_apply_rule_at = NOT_SET
    _variables_help = """Replace XXX_performance with any combination of:
                      batting_performance, bowling_performance,
                      fielding_performance, player_match_stats"""
    _variables_default = "rule, XXX_performance"
    _calculations_default = "rule.points_or_factor if XXX_performance else 0"

    _can_be_default = False

    rule_applications = (
        (PLAYER_SCORING, "When scoring a Player Performance"),
        (MEMBER_PREDICTION_VALIDATION, "When validating a Member Prediction"),
        (MEMBER_PREDICTION_SCORING, "When scoring a Member Prediction"),
        (
            POST_MATCH_PREDICTION_SCORING,
            """Apply after Match is finished and
                                        all Predictions have been scored""",
        ),
        (LEADERBOARD_SCORING, "Apply on Leaderboards"),
        (TOURNAMENT_SCORING, "Apply on Tournaments"),
    )

    rule_apply_to_clones_choices = (
        (DO_NOT_APPLY_CHANGES_TO_CLONES, "----"),
        (APPLY_CHANGES_TO_CLONES, "Apply these changes to ALL clones of this rule."),
    )

    category_choices = (
        (CAT_NOT_SET, "---"),
        (BATTING_CATEGORY, "Batting Points"),
        (BOWLING_CATEGORY, "Bowling Points"),
        (FIELDING_CATEGORY, "Fielding Points"),
        (TEAM_CATEGORY, "Team Points"),
        (GENERAL_CATEGORY, "General Points"),
    )

    match_types = ((ONE_DAY, "One Day"), (T_TWENTY, "T-20"), (TEST, "Test Match"))

    points_display_choices = (
        (DISPLAY_POINTS, "Points"),
        (DISPLAY_FACTOR, "Factor"),
        (DISPLAY_RANGES, "Range"),
    )

    match_types_short_names = {ONE_DAY: "OD", T_TWENTY: "T20", TEST: "TEST"}

    name = models.CharField(max_length=100, blank=False, null=False)

    description = models.TextField(max_length=500, null=True, blank=True)

    enable_for_matches = PythonCodeField(
        max_length=50,
        null=False,
        blank=False,
        default=MATCH_NUMBER_CHECK_LAMBDA_STR,
        validators=[is_code_and_lambda],
        help_text="e.g. lambda match: match.match_number in [1,2,3]",
    )

    apply_rule_at = models.IntegerField(
        blank=False,
        null=False,
        default=_default_apply_rule_at,
        choices=rule_applications,
        help_text="When to apply a rule (automatically set on save).",
    )

    variables = PythonCodeField(
        max_length=100,
        blank=False,
        null=False,
        default=_variables_default,
        help_text=_variables_help,
    )

    functions = PythonCodeField(max_length=1000, null=True, blank=True)

    calculation = PythonCodeField(
        max_length=750, blank=False, null=False, default=_calculations_default
    )

    points_or_factor = models.IntegerField(blank=False, null=False, default=0)
    is_default = models.BooleanField(blank=False, null=False, default=False)
    is_enabled = models.BooleanField(blank=False, null=False, default=True)
    notes = models.TextField(max_length=100, blank=True, null=True)

    apply_changes_to_cloned_rules = models.BooleanField(
        blank=False,
        null=False,
        default=DO_NOT_APPLY_CHANGES_TO_CLONES,
        choices=rule_apply_to_clones_choices,
    )

    rule_category = models.IntegerField(
        blank=False, default=CAT_NOT_SET, choices=category_choices
    )
    display_order = models.IntegerField(blank=False, default=0, null=False)
    display_points_as = models.IntegerField(
        blank=False, default=DISPLAY_POINTS, null=False
    )
    apply_to_match_type = models.IntegerField(
        blank=False, default=T_TWENTY, null=False, choices=match_types
    )

    def __str__(self):
        return "{} ({} id={})".format(
            self.name, Rule.match_types_short_names[self.apply_to_match_type], self.id
        )

    def save(self, *args, **kwargs):
        # Reach down and apply properties from child classes
        setattr(self, "apply_rule_at", self._default_apply_rule_at)

        if not self._can_be_default:
            setattr(self, "is_default", False)

        super(Rule, self).save(*args, **kwargs)

        # Update rules that have been cloned from a parent one
        if self.apply_changes_to_cloned_rules:
            rule_klass = type(self)
            if rule_klass in DEFAULT_RULE_TYPES:
                apply_changes_to_clones(self)

            self.apply_changes_to_cloned_rules = Rule.DO_NOT_APPLY_CHANGES_TO_CLONES

            self.save()

    def category_name(self):
        for id, name in self.category_choices:
            if id == self.rule_category:
                return name

    class Meta:
        abstract = True


class RuleRange(models.Model):
    range_description = models.CharField(max_length=200, null=False, blank=False)
    points = models.IntegerField(null=False, blank=False)

    class Meta:
        verbose_name_plural = "Rule Ranges"
        abstract = True

    def __str__(self):
        return "Range: {self.rule.name, (rID={self.rule.id})}"


class PlayerScoringMethod(Rule):
    _default_apply_rule_at = Rule.PLAYER_SCORING
    _can_be_default = True

    apply_on_batting_performance = models.BooleanField(
        blank=False, null=False, default=False
    )
    apply_on_bowling_performance = models.BooleanField(
        blank=False, null=False, default=False
    )
    apply_on_fielding_performance = models.BooleanField(
        blank=False, null=False, default=False
    )
    apply_on_match_performance = models.BooleanField(
        blank=False, null=False, default=False
    )


class R1(RuleRange):
    rule = models.ForeignKey(
        PlayerScoringMethod, null=False, blank=False, on_delete=models.PROTECT
    )


class PredictionScoringMethod(Rule):
    _default_apply_rule_at = Rule.MEMBER_PREDICTION_SCORING
    _can_be_default = True
    _variables_default = "rule, prediction, match"
    _variables_help = ""
    _calculations_default = "rule.points_or_factor if prediction else 0"


class R2(RuleRange):
    rule = models.ForeignKey(
        PredictionScoringMethod, null=False, blank=False, on_delete=models.PROTECT
    )


class PredictionSubmissionValidationRule(Rule):
    _default_apply_rule_at = Rule.MEMBER_PREDICTION_VALIDATION
    _can_be_default = True

    MATCH_DATA_SUBMISSION = 1
    TOURNAMENT_DATA_SUBMISSION = 2

    type_choices = (
        (MATCH_DATA_SUBMISSION, "Match"),
        (TOURNAMENT_DATA_SUBMISSION, "Tournament"),
    )

    apply_to_submission_type = models.IntegerField(
        null=False, blank=False, choices=type_choices
    )


class PostMatchPredictionScoringMethod(Rule):
    _default_apply_rule_at = Rule.POST_MATCH_PREDICTION_SCORING
    _can_be_default = True


class LeaderBoardScoringMethod(Rule):
    _default_apply_rule_at = Rule.LEADERBOARD_SCORING
    _can_be_default = True


class TournamentScoringMethod(Rule):
    _default_apply_rule_at = Rule.TOURNAMENT_SCORING
    _can_be_default = True


class GroupTournamentScoringMethod(Rule):
    _default_apply_rule_at = Rule.TOURNAMENT_SCORING

    parent_rule = models.ForeignKey(
        TournamentScoringMethod, null=False, blank=False, on_delete=models.PROTECT
    )

    def __str__(self):
        e = "E" if self.is_enabled else "D"
        return "{} (gr-id={} ({}))".format(self.name, self.id, e)


class GroupLeaderBoardScoringMethod(Rule):
    _default_apply_rule_at = Rule.LEADERBOARD_SCORING

    parent_rule = models.ForeignKey(
        LeaderBoardScoringMethod, null=False, blank=False, on_delete=models.PROTECT
    )

    def __str__(self):
        e = "E" if self.is_enabled else "D"
        return "{} (gr-id={} ({}))".format(self.name, self.id, e)


class GroupPredictionSubmissionValidationRule(Rule):
    _default_apply_rule_at = Rule.MEMBER_PREDICTION_VALIDATION

    MATCH_DATA_SUBMISSION = 1
    TOURNAMENT_DATA_SUBMISSION = 2

    type_choices = (
        (MATCH_DATA_SUBMISSION, "Match"),
        (TOURNAMENT_DATA_SUBMISSION, "Tournament"),
    )

    parent_rule = models.ForeignKey(
        PredictionSubmissionValidationRule,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
    )

    apply_to_submission_type = models.IntegerField(
        null=False, blank=False, choices=type_choices
    )

    def __str__(self):
        e = "E" if self.is_enabled else "D"
        return "{} (gr-id={} ({}))".format(self.name, self.id, e)


class GroupPlayerScoringMethod(Rule):
    _default_apply_rule_at = Rule.PLAYER_SCORING

    apply_on_batting_performance = models.BooleanField(
        blank=False, null=False, default=False
    )
    apply_on_bowling_performance = models.BooleanField(
        blank=False, null=False, default=False
    )
    apply_on_fielding_performance = models.BooleanField(
        blank=False, null=False, default=False
    )
    apply_on_match_performance = models.BooleanField(
        blank=False, null=False, default=False
    )

    parent_rule = models.ForeignKey(
        PlayerScoringMethod, null=False, blank=False, on_delete=models.PROTECT
    )

    def __str__(self):
        e = "E" if self.is_enabled else "D"
        return "{} (gr-id={} ({}))".format(self.name, self.id, e)


class GroupPredictionScoringMethod(Rule):
    _default_apply_rule_at = Rule.MEMBER_PREDICTION_SCORING
    _can_be_default = True
    _variables_default = "rule, prediction, match"
    _variables_help = ""
    _calculations_default = "rule.points_or_factor if prediction else 0"

    parent_rule = models.ForeignKey(
        PredictionScoringMethod, null=False, blank=False, on_delete=models.PROTECT
    )

    def __str__(self):
        e = "E" if self.is_enabled else "D"
        return "{} (gr-id={} ({}))".format(self.name, self.id, e)


class GroupPostMatchPredictionScoringMethod(Rule):
    _default_apply_rule_at = Rule.POST_MATCH_PREDICTION_SCORING

    parent_rule = models.ForeignKey(
        PostMatchPredictionScoringMethod,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        e = "E" if self.is_enabled else "D"
        return "{} (gr-id={} ({}))".format(self.name, self.id, e)


class RuleResult(models.Model):
    class Meta:
        abstract = True

    # Store this as it could be useful during a result's lifetime
    rule_variables_and_values = {}

    input_values = models.TextField(
        max_length=1000, blank=False, null=False, default=""
    )
    calculation = models.TextField(max_length=750, blank=False, null=False, default="")
    points_or_factor = models.IntegerField(blank=False, null=False, default=0)
    computed_on = models.DateTimeField(null=False, auto_now_add=True)
    result = models.CharField(max_length=20, null=False, blank=False, default="0")
    error_message = models.TextField(null=True, editable=False)

    def __str__(self):
        return "Rule={}, score={}".format(self.rule, self.result)

    def rule_name(self):
        return self.rule.name


class PlayerScoringResult(RuleResult):
    rule = models.ForeignKey(
        PlayerScoringMethod, related_name="+", on_delete=models.PROTECT
    )


class PredictionScoringResult(RuleResult):
    rule = models.ForeignKey(
        PredictionScoringMethod, related_name="+", on_delete=models.PROTECT
    )


class PredictionValidationResult(RuleResult):
    rule = models.ForeignKey(
        PredictionSubmissionValidationRule, related_name="+", on_delete=models.PROTECT
    )


class PostMatchPredictionScoringMethodResult(RuleResult):
    rule = models.ForeignKey(
        PostMatchPredictionScoringMethod, related_name="+", on_delete=models.PROTECT
    )


class LeaderBoardScoringMethodResult(RuleResult):
    rule = models.ForeignKey(
        LeaderBoardScoringMethod, related_name="+", on_delete=models.PROTECT
    )


class TournamentScoringMethodResult(RuleResult):
    rule = models.ForeignKey(
        TournamentScoringMethod, related_name="+", on_delete=models.PROTECT
    )


class GroupTournamentScoringMethodResult(RuleResult):
    rule = models.ForeignKey(
        GroupTournamentScoringMethod, related_name="+", on_delete=models.PROTECT
    )


class GroupLeaderBoardScoringMethodResult(RuleResult):
    rule = models.ForeignKey(
        GroupLeaderBoardScoringMethod, related_name="+", on_delete=models.PROTECT
    )


class GroupPlayerScoringResult(RuleResult):
    rule = models.ForeignKey(
        GroupPlayerScoringMethod, related_name="+", on_delete=models.PROTECT
    )


class GroupPredictionScoringResult(RuleResult):
    rule = models.ForeignKey(
        GroupPredictionScoringMethod, related_name="+", on_delete=models.PROTECT
    )


class GroupPredictionSubmissionValidationResult(RuleResult):
    rule = models.ForeignKey(
        GroupPredictionSubmissionValidationRule,
        related_name="+",
        on_delete=models.PROTECT,
    )


class GroupPostMatchPredictionScoringMethodResult(RuleResult):
    rule = models.ForeignKey(
        GroupPostMatchPredictionScoringMethod,
        related_name="+",
        on_delete=models.PROTECT,
    )


DEFAULT_RULE_TYPES = [
    PredictionScoringMethod,
    PlayerScoringMethod,
    PredictionSubmissionValidationRule,
    PostMatchPredictionScoringMethod,
    LeaderBoardScoringMethod,
    TournamentScoringMethod,
]

RULE_TYPES = DEFAULT_RULE_TYPES + [
    GroupPlayerScoringMethod,
    GroupPredictionScoringMethod,
    GroupPredictionSubmissionValidationRule,
    GroupPostMatchPredictionScoringMethod,
    GroupLeaderBoardScoringMethod,
    GroupTournamentScoringMethod,
]

# Dict is {}
# master_rule class : (group_rule class,
#               corresponding variable in MemberGroupRules
#               that holds group_rule equilvalent of master_rule),
RULE_TO_MEMBER_GROUP_RULE_MAPPING = {
    PlayerScoringMethod: (GroupPlayerScoringMethod, "group_player_scoring_rules"),
    PredictionScoringMethod: (
        GroupPredictionScoringMethod,
        "group_prediction_scoring_rules",
    ),
    PredictionSubmissionValidationRule: (
        GroupPredictionSubmissionValidationRule,
        "group_submission_validation_rules",
    ),
    PostMatchPredictionScoringMethod: (
        GroupPostMatchPredictionScoringMethod,
        "group_post_match_prediction_scoring_rules",
    ),
    LeaderBoardScoringMethod: (
        GroupLeaderBoardScoringMethod,
        "group_leaderboard_scoring_rules",
    ),
    TournamentScoringMethod: (
        GroupTournamentScoringMethod,
        "group_tournament_scoring_rules",
    ),
}

reversion.register(PlayerScoringMethod)
reversion.register(PredictionScoringMethod)
reversion.register(PredictionSubmissionValidationRule)
reversion.register(PostMatchPredictionScoringMethod)
reversion.register(PlayerScoringResult)
reversion.register(PredictionScoringResult)
reversion.register(PredictionValidationResult)
reversion.register(PostMatchPredictionScoringMethodResult)
reversion.register(TournamentScoringMethod)
reversion.register(LeaderBoardScoringMethod)

reversion.register(GroupPlayerScoringMethod)
reversion.register(GroupPredictionScoringMethod)
reversion.register(GroupPredictionSubmissionValidationRule)
reversion.register(GroupPostMatchPredictionScoringMethod)
reversion.register(GroupPlayerScoringResult)
reversion.register(GroupPredictionScoringResult)
reversion.register(GroupPredictionSubmissionValidationResult)
reversion.register(GroupPostMatchPredictionScoringMethodResult)
reversion.register(GroupTournamentScoringMethod)
