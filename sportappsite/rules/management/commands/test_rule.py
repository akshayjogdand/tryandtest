import argparse

from django.core.management.base import BaseCommand, CommandError

from rules.models import (
    PlayerScoringMethod,
    PredictionScoringMethod,
    PredictionSubmissionValidationRule,
)

from scoring.scoring import run_rule, RuleError, mk_class_obj


def nested_check(instr, value, root):
    object_elements = instr.split(".")

    if len(object_elements) == 1:
        setattr(root, instr, value)

    else:
        # winning_team.squad.score, final name is score
        final_name = object_elements.pop()

        parent = root
        # first pass sets 'winning_team', second pass sets 'squad'..
        for name in object_elements:
            setattr(parent, name, mk_class_obj(name))
            parent = getattr(parent, name)

        # ... and this sets winning_team.squad.score
        setattr(parent, final_name, value.strip())

    return root


def check_input_vars(arg):
    values = arg.strip().split("=")
    if len(values) != 2 or "=" not in arg:
        argparse.ArgumentTypeError(
            "Arguments need to be supplied in the"
            "format: var_name=value, you gave {}".format(arg)
        )

    var, value = values
    if var.isnumeric():
        raise argparse.ArgumentError(
            "Variable needs to be a string, you gave: {}".format(arg)
        )

    elif value.startswith("{") and value.endswith("}"):
        l = value.replace("{", "").replace("}", "").split(",")
        o = mk_class_obj(var.strip())
        for attr_value_str in l:
            k, v = attr_value_str.strip().split(":")
            parsed_value = nested_check(k.strip(), v.strip(), o)

        return (var.strip(), parsed_value)
    else:
        return (var.strip(), value.strip())


def get_rule_type(arg):
    mapping = {
        "1": PlayerScoringMethod,
        "2": PredictionScoringMethod,
        "3": PredictionSubmissionValidationRule,
    }
    return mapping[arg.strip()]


class Command(BaseCommand):
    help = "Execute a single rule, printing it's resulting score"

    def add_arguments(self, parser):
        parser.add_argument(
            "--rule-type",
            required=True,
            type=get_rule_type,
            help="Rule Type you are trying to test, choose number: "
            "1 = PlayerScoringMethod,"
            "2 = PredcitionScoringMethod,"
            "3 = PredcitionValidationRule",
        )

        parser.add_argument(
            "--rule-id", required=True, type=int, help="Rule ID to test"
        )

        parser.add_argument(
            "--input-values",
            required=True,
            type=check_input_vars,
            nargs="+",
            help="Values to test rule against. " "Provide like: var1=val1 var2=val2...",
        )

    def handle(self, rule_id, rule_type, input_values, **options):
        try:
            rule = rule_type.objects.get(pk=rule_id)
            combined_inputs = {}
            for var, value in input_values:
                combined_inputs[var] = value

            rule_result = run_rule(rule, combined_inputs)

        except (
            PlayerScoringMethod.DoesNotExist,
            PredictionScoringMethod.DoesNotExist,
            PredictionSubmissionValidationRule.DoesNotExist,
        ) as ex:
            raise CommandError(
                "{} with id: {} " "does not exist".format(str(ex).split()[0], rule_id)
            )
        except RuleError as e:
            raise CommandError(e)

        self.stdout.write(
            "Testing rule: '{}', id={} \n" "INPUT:\n".format(rule.name, rule.id)
        )
        for k, v in rule_result.rule_variables_and_values.items():
            self.stdout.write("\t{}:  {}".format(k, v))

        self.stdout.write("RESULT is: {}".format(rule_result.result))
