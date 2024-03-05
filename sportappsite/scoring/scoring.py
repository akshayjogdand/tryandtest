from collections import Counter

import types

import math

import re

from inspect import signature

import logging

from stats.models import (
    BattingPerformance,
    BowlingPerformance,
    FieldingPerformance,
    MatchPerformance,
)

from predictions.models import MemberPrediction

from fixtures.models import Match

from rules.models import Rule, RuleResult


DISALLOWED_GLOBALS = [
    "compile",
    "eval",
    "DISALLOWED_GLOBALS",
    "exit",
    "input",
    "exec",
    "globals",
    "locals",
    "open",
    "type",
    "types",
    "re",
    "signature",
]

ALLOWED_GLOBALS = dict(
    [
        (k, globals().get("__builtins__").get(k))
        for k in globals().get("__builtins__")
        if k not in DISALLOWED_GLOBALS
    ]
)


logger = logging.getLogger("rules_execution")


class RuleError(Exception):
    pass


# A class that can be used to construct arbitary objects out of
# parsed string data
class StringArguments(types.SimpleNamespace):
    pass


PLAYER_PERFORMANCE_TYPES = (
    BattingPerformance,
    BowlingPerformance,
    FieldingPerformance,
    MatchPerformance,
)

ALLOWED_VALUE_TYPES = [
    int,
    str,
    bool,
    float,
    Match,
    MemberPrediction,
    StringArguments,
].extend(PLAYER_PERFORMANCE_TYPES)

ALLOWED_BOOLEAN_VALUE_STRINGS = ("true", "false")


def mk_class_obj(cname):
    return types.new_class(cname, (StringArguments,))()


def get_rule_variables(rule):
    return [v.strip() for v in rule.variables.split(",")]


def convert_value(value):
    val = value
    value_type = type(value)

    # msg = '''Variable value types allowed are:
    # [float, +ive int, (Boolean | Match |
    # MemberPrediction)  objects, Strings('true',| 'false')
    # \nYou provided: {}'''

    # if value_type not in ALLOWED_VALUE_TYPES:
    #     raise RuleError(msg.format(value_type))

    if isinstance(value, StringArguments):
        for attr, attr_value in vars(value).items():
            setattr(value, attr, convert_value(attr_value))

    elif value_type is int:
        val = abs(int(value))

    elif value_type is float:
        val = value

    # Try and crack out types from a string
    elif value_type is str:
        if value.isnumeric():
            val = abs(int(value))

        elif value.count(".") == 1:
            try:
                val = float(value)
            except ValueError:
                pass

        elif value.lower() in ALLOWED_BOOLEAN_VALUE_STRINGS:
            val = value.lower() == "true" and True or False

        else:
            raise (
                RuleError(
                    "Provided String value: '{}' is not allowed. \n"
                    "\t\tAllowed strings are: {}".format(
                        value, ALLOWED_BOOLEAN_VALUE_STRINGS
                    )
                )
            )

    elif value_type is bool:
        val = value

    return val


def extract_rule_variables_from_object(rule, value_object):
    strs = ["[", "{}(id={}):".format(type(value_object).__name__, value_object.id)]

    for k, v in vars(value_object).items():
        if ".{}".format(k) in rule.calculation:

            strs.append("{}={}".format(k, v))

    strs.append("]")
    return " ".join(strs)


def stringyfy(some_dict, rule):
    strs = []

    for k, v in some_dict.items():
        if isinstance(v, Rule):
            pass

        elif k == "__builtins__":
            pass

        elif isinstance(v, Match):
            strs.append("[Match id: {}, ]".format(v.id))

        elif isinstance(v, MemberPrediction):
            strs.append(extract_rule_variables_from_object(rule, v))

        elif isinstance(v, StringArguments):
            strs.append(k + "." + (stringyfy(vars(v), rule)))

        elif isinstance(v, PLAYER_PERFORMANCE_TYPES):
            strs.append(extract_rule_variables_from_object(rule, v))

        else:
            strs.append("{}: {}".format(k, v))

    strs.append(
        "[{}(id={}): points_or_factor={}]".format(
            type(rule).__name__, rule.id, rule.points_or_factor
        )
    )
    return ", ".join(strs)


def clean(text):
    x = text.strip()
    x = re.sub("\r\n", " ", x)
    x = re.sub("\n", " ", x)
    x = re.sub("\r", " ", x)
    return re.sub("\s{2,}", " ", x)


def callable_to_invocation_string(func, func_name):
    fs = "{}({})".format(func_name, "{}")
    return fs.format(",".join([*signature(func).parameters]))


def run_rule(rule, inputs, result_klass=RuleResult):
    logger.debug("Running rule: {}".format(rule.name))

    rule_variables = get_rule_variables(rule)
    formula = clean(rule.calculation)
    rule_variables_and_values = {}

    if rule.functions is not None:
        rule_variables_and_values["__builtins__"] = ALLOWED_GLOBALS.copy()
        rule_variables_and_values["math"] = math
        rule_variables_and_values["Counter"] = Counter
        # rule_variables_and_values['logger'] = logger

        exec(rule.functions, rule_variables_and_values)

    if "rule" in rule_variables:
        inputs["rule"] = rule

    for variable in rule_variables:
        if variable not in inputs:
            raise RuleError(
                """Variable '{}' required by rule: '{}' has not been provided.
                 \n Provided variables are: {}""".format(
                    variable, rule.name, inputs.keys()
                )
            )

        rule_variables_and_values[variable] = convert_value(inputs[variable])

    rr = result_klass()
    rr.rule = rule
    rr.input_values = stringyfy(rule_variables_and_values, rule)
    rr.points_or_factor = rule.points_or_factor

    try:
        rr.result = eval(formula, None, rule_variables_and_values)
        rr.calculation = formula
        rr.rule_variables_and_values = rule_variables_and_values

        if rr.result is False and "error_message_function" in rule_variables_and_values:
            error_fn_call = callable_to_invocation_string(
                rule_variables_and_values["error_message_function"],
                "error_message_function",
            )
            rr.error_message = eval(error_fn_call, None, rule_variables_and_values)

    except AttributeError as e:
        exception_message = e.args[0]
        variable_value = e.args[0].split()[0]

        msg = """{}\n\tCheck variable: =={}== in calculation
              or inputs, Rule={}""".format(
            exception_message, variable_value, rule
        )

        raise RuleError(msg)

    except Exception as e:
        print("\n\n\tERROR: running rule: {}\n\tformula: {}\n".format(rule, formula))
        print("Inputs provided:")
        print("================")
        for k, v in rule_variables_and_values.items():
            print("{}: {}".format(k, v))
        print("\nException was: {}".format(e))
        print("\n")
        raise e

    return rr
