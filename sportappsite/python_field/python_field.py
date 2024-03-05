from django.db import models
from django import forms

import six


class PythonCodeWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super(PythonCodeWidget, self).__init__(*args, **kwargs)
        self.attrs["class"] = "python-code"
        self.attrs["style"] = "width: 50%; height: 100%;"

    class Media:
        css = {
            "all": (
                "/static/codemirror-5.25.0/codemirror.css",
                "/static/codemirror-5.25.0/addon/fold/foldgutter.css",
                "/static/codemirror-5.25.0/theme/eclipse.css",
            )
        }
        js = (
            "/static/codemirror-5.25.0/codemirror.js",
            "/static/codemirror-5.25.0/mode/python/python.js",
            "/static/codemirror-5.25.0/addon/edit/matchbrackets.js",
            "/static/codemirror-5.25.0/addon/edit/closebrackets.js",
            "/static/codemirror-5.25.0/addon/edit/trailingspace.js",
            "/static/codemirror-5.25.0/addon/fold/foldgutter.js",
            "/static/codemirror-5.25.0/addon/fold/foldcode.js",
            "/static/codemirror-5.25.0/addon/fold/brace-fold.js",
            "/static/codemirror-5.25.0/addon/fold/comment-fold.js",
            "/static/codemirror-5.25.0/addon/fold/indent-fold.js",
            "/static/codemirror-5.25.0/addon/selection/active-line.js",
            "/static/codemirror-5.25.0/addon/selection/mark-selection.js",
            "/static/codemirror-5.25.0/init.js",
        )


class PythonCodeFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = PythonCodeWidget
        super(PythonCodeFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        """
        We need to ensure that the code that was entered validates as
        python code.
        """

        if not value:
            return

        if isinstance(value, six.string_types):
            try:
                value = value.replace("\r", "")
                compile(value, "<string>", "exec")
            except SyntaxError as e:
                raise forms.ValidationError(u"Syntax Error: %s" % (e))
            return value


class PythonCodeField(models.TextField):
    """
    A field that will ensure that data that is entered into it is syntactically
    valid python code.
    """

    description = "Python Source Code"

    def formfield(self, **kwargs):
        return super(PythonCodeField, self).formfield(
            form_class=PythonCodeFormField, **kwargs
        )

    def from_db_value(self, value, expression, connection, context=None):
        return value

    def to_python(self, value):
        return value
