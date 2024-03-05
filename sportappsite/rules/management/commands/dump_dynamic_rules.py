import os
import re

from django.core.management.base import BaseCommand

from rules.models import RULE_TO_MEMBER_GROUP_RULE_MAPPING

RULE_APPLICATION = {
    -1: "NOT_SET",
    0: "PLAYER_SCORING",
    1: "MEMBER_PREDICTION_VALIDATION",
    2: "MEMBER_PREDICTION_SCORING",
    3: "POST_MATCH_PREDICTION_SCORING",
    4: "LEADERBOARD_SCORING",
    5: "TOURNAMENT_SCORING",
}

MATCH_TYPES = {1: "ONE_DAY", 2: "T_TWENTY", 3: "TEST"}


def ensure_rule_folder_exists(base_path, rule, parent_rule_name):
    file_path = "{}/{}/rule_{}".format(base_path, parent_rule_name, rule.id)

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    return file_path


def prepare_rule_file_data(rule):
    rule_data = ""

    try:
        rule_data += "#{}\n".format(RULE_APPLICATION[rule.apply_rule_at])
    except:
        pass

    rule_data += "apply_rule_at = {}\n\n".format(rule.apply_rule_at)
    rule_data += "points_or_factor = {}\n".format(rule.points_or_factor)
    rule_data += "rule_category = {}\n".format(rule.rule_category)

    try:
        rule_data += "\n#{}\n".format(MATCH_TYPES[rule.apply_to_match_type])
    except:
        pass
    rule_data += "apply_to_match_type = {}\n\n".format(rule.apply_to_match_type)

    rule_variables = rule.variables.strip(" , ").split(", ")
    rule_data += "variables = {}\n\n".format(tuple(rule_variables))

    rule_data += "enable_for_matches = {}\n\n".format(rule.enable_for_matches)

    func_str = f"\n{rule.functions}\n"
    rule_data += func_str

    rule_data += "calculation = lambda : {} \n\n".format(rule.calculation)

    return rule_data


def write_rule_data(file_path, file_data, parent_rule, parent_rule_name):
    name = parent_rule.name.replace("+", "")
    name = name.replace("/", "")
    name = name.replace("-", "")
    # windows don't allow this character to be in file name
    name = re.sub(r'[<>:\/?*"|]', "", name)
    name = name.replace(" ", "_")

    file_name = """{}/{}.py""".format(file_path, name)
    rule_file = open(file_name, "w")
    rule_file.write(file_data)


class Command(BaseCommand):
    help = "Generate textual dump of all dynamic rules"

    def handle(self, *args, **kwargs):
        rule_corpus_path = "rules/corpus"
        if not os.path.exists(rule_corpus_path):
            os.makedirs(rule_corpus_path)

        for parent_rule_class in RULE_TO_MEMBER_GROUP_RULE_MAPPING.keys():
            parent_rule_name = parent_rule_class.__name__
            for rule in parent_rule_class.objects.all():
                f_path = ensure_rule_folder_exists(
                    rule_corpus_path, rule, parent_rule_name
                )
                rule_file_data = prepare_rule_file_data(rule)
                write_rule_data(f_path, rule_file_data, rule, parent_rule_name)

        return print("All parent rules are dumped")
