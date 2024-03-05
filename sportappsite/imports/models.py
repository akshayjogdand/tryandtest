from django.db import models

from fixtures.models import Match

from members.models import MemberGroup


class DataImport(models.Model):
    IMPORT_MATCH_DATA = 0
    IMPORT_BATTING_PERFORMANCE = 1
    IMPORT_BOWLING_PERFORMANCE = 2
    IMPORT_FIELDING_PERFORMANCE = 3
    IMPORT_MATCH_PERFORMANCE = 4
    IMPORT_MEMBER_PREDICTIONS = 5

    import_choices = (
        (IMPORT_MATCH_DATA, "Match data"),
        (IMPORT_BATTING_PERFORMANCE, "Batting Performance"),
        (IMPORT_BOWLING_PERFORMANCE, "Bowling Performance"),
        (IMPORT_FIELDING_PERFORMANCE, "Fielding Performance"),
        (IMPORT_MATCH_PERFORMANCE, "Match Performance"),
        (IMPORT_MEMBER_PREDICTIONS, "Member Predictions"),
    )

    description = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        default="--",
        help_text="Auto set on save.",
    )
    import_type = models.IntegerField(null=False, blank=False, choices=import_choices)
    data_file = models.FileField(upload_to="import_uploads/%Y/%m/%d/")
    match = models.ForeignKey(Match, blank=False, null=False, on_delete=models.PROTECT)
    imported_on = models.DateTimeField(auto_now_add=True, null=False, blank=True)
    member_group = models.ForeignKey(
        MemberGroup, null=True, blank=True, on_delete=models.PROTECT
    )
    notes = models.TextField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.description

    def mk_description(self):
        value = "{} CSV for {}, match-{}"

        if self.import_type == self.IMPORT_MATCH_DATA:
            desc = value.format(
                "Match data", self.match.tournament, self.match.match_number
            )
        elif self.import_type == self.IMPORT_BATTING_PERFORMANCE:
            desc = value.format(
                "Batting Performance data",
                self.match.tournament,
                self.match.match_number,
            )
        elif self.import_type == self.IMPORT_BOWLING_PERFORMANCE:
            desc = value.format(
                "Bowling Performance data",
                self.match.tournament,
                self.match.match_number,
            )
        elif self.import_type == self.IMPORT_FIELDING_PERFORMANCE:
            desc = value.format(
                "Fielding Performance data",
                self.match.tournament,
                self.match.match_number,
            )
        elif self.import_type == self.IMPORT_MATCH_PERFORMANCE:
            desc = value.format(
                "Match Performance data", self.match.tournament, self.match.match_number
            )
        elif self.import_type == self.IMPORT_MEMBER_PREDICTIONS:
            desc = "{}, {}".format(
                self.member_group.group.name,
                value.format(
                    "Member Predictions data",
                    self.match.tournament,
                    self.match.match_number,
                ),
            )

        return desc

    def save(self, *args, **kwargs):
        if self.description == "--":
            setattr(self, "description", self.mk_description())
        super(DataImport, self).save(*args, **kwargs)
