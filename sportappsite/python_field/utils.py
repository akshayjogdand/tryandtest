from django.core.exceptions import ValidationError


def is_code_and_lambda(value, test_string="lambda "):
    if value == "" or value is None:
        raise ValidationError("This value cannot be blank.")

    elif not value.startswith(test_string):
        raise ValidationError("Check has to be simple lambda function")

    else:
        try:
            compile(value, "string", "single")
        except Exception as exp:
            raise ValidationError(exp)


def is_dict(value):
    if value == "" or value is None:
        raise ValidationError("This value cannot be blank.")

    else:
        try:
            compile(value, "string", "single")
        except Exception as exp:
            raise ValidationError(exp)
