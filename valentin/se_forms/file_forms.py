from django import forms
from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation, ValidationError

"""
Exceptions
"""


class MalformedForm(ValidationError):
    pass


class MalformedQuestion(MalformedForm):
    pass


class MalformedQuestionChoice(MalformedQuestion):
    pass


class DynamicForm(forms.Form):
    def __init__(self, *args, **kwargs):
        extracted_fields = kwargs.pop("extracted_fields", None)
        super(DynamicForm, self).__init__(*args, **kwargs)
        if extracted_fields:
            for id, field in extracted_fields:
                self.fields[id] = field


class QuestionFieldBuilder:
    FIELD_TYPES = {
        # field type in raw data : function identifier inside this class
        "choice": "get_choice_field",
        "multiple_choices": "get_multiple_choices_field",
        "text": "get_char_field",
        "integer": "get_integer_field",
        "long_text": "get_long_text_field",
    }

    def __init__(self, data):
        self.data = data

    @staticmethod
    def get_sanitized_choices(data):
        choices = None
        try:
            choices = data["choices"]
        except KeyError:
            raise MalformedQuestion(
                "choice-based question does not contains choices list"
            )

        if not isinstance(choices, list):
            raise MalformedQuestion("Choices must be an array")

        cleaned_choices = []

        for choice in choices:
            if not isinstance(choice, dict):
                raise MalformedQuestionChoice("Choice element must be a dict")
            try:
                cleaned_choices.append((str(choice["id"]), str(choice["text"])))
            except KeyError:
                raise MalformedQuestionChoice(
                    "Choice element must contain at least id and text"
                )
            except:  # NOQA
                # if someone has a better idea please go PR
                raise MalformedQuestionChoice(
                    "Choice elements id and text must be stringable"
                )

        return tuple(cleaned_choices)

    @classmethod
    def get_choice_field(cls, data):
        choices = cls.get_sanitized_choices(data)
        return forms.ChoiceField(
            choices=choices,
            required=False,
            widget=forms.RadioSelect(),
            help_text=str(data.get("help_text")),
            label=str(data["text"]),
        )

    @classmethod
    def get_multiple_choices_field(cls, data):
        choices = cls.get_sanitized_choices(data)
        return forms.MultipleChoiceField(
            choices=choices,
            required=False,
            widget=forms.CheckboxSelectMultiple(),
            help_text=str(data.get("help_text")),
            label=str(data["text"]),
        )

    @staticmethod
    def get_char_field(data):
        return forms.CharField(
            max_length=int(data["max_length"]),
            min_length=int(data.get("min_length", 0)),
            help_text=str(data.get("help_text")),
            required=False,
            label=str(data["text"]),
        )

    @staticmethod
    def get_integer_field(data):
        return forms.IntegerField(
            max_value=int(data["max_value"]),
            min_value=int(data.get("min_value", 0)),
            help_text=str(data.get("help_text")),
            required=False,
            label=str(data["text"]),
        )

    @staticmethod
    def get_long_text_field(data):
        return forms.CharField(
            widget=forms.Textarea(),
            max_length=int(data["max_length"]),
            min_length=int(data.get("min_length", 0)),
            help_text=str(data.get("help_text")),
            label=str(data["text"]),
            required=False,
        )

    @classmethod
    def get_field_converter_from_string(cls, field_type):
        try:
            func = getattr(cls, cls.FIELD_TYPES[field_type])
            if not callable(func):
                raise TypeError("FIELD_TYPES values must be callable")
            return func
        except AttributeError:
            raise NotImplementedError(
                "Callable mentioned in FIELD_TYPES does not exist in class"
            )
        except KeyError:
            raise MalformedQuestion("Question type is not valid")

    def build(self):
        """
        Takes question dict and return (question_id, django_formfield) \in (str, django.Forms.Field)
        may raise se_forms.MalformedQuestion when the code is OK.

        However if the code happens to not be ok it may raise TypeError and/or NotImplementedError
        (see get_field_converter_from_string for more insight on this)
        """

        question = self.data

        if not isinstance(question, dict):
            raise MalformedQuestion("Question must be a dict")

        try:
            self.id = str(question["id"])
            self.type = str(question["type"])
        except KeyError:
            raise MalformedQuestion("Question fields id and type are required")
        except:  # NOQA
            raise MalformedQuestion("Question fields id and type must be stringable")

        try:
            self.form_field = self.get_field_converter_from_string(self.type)(question)
        except KeyError as ke:
            raise MalformedQuestion(
                f"Question {self.id} is missing mandatory key {str(ke)}"
            )
        except MalformedQuestionChoice as e:
            raise MalformedQuestionChoice(f"Question {self.id} : {str(e)}")
        return (self.id, self.form_field)


class FormBuilder:
    """
    This class builds a django.forms.Form (unbound) from dict-like objects
    that follows a specific schema.
    """

    """
    (name, type_converter_function, default)
    default == NotImplemented <=> required metadata
    reserved keywords : questions
    """
    METADATA = (
        ("title", str, NotImplemented),
        ("introduction", str, None),
    )

    def __init__(self, raw_data):
        self.raw_data = raw_data

    def populate_metadata(self):
        for name, conv, default in self.METADATA:
            if default is NotImplemented and not self.raw_data.get(name):
                raise MalformedForm(f"Missing mandatory metadata {name}")

            setattr(self, name, conv(self.raw_data.get(name, default)))

    def build(self):
        if not isinstance(self.raw_data, dict):
            raise MalformedForm("raw_data root must be a dict")

        self.populate_metadata()

        questions = None
        try:
            questions = self.raw_data["questions"]
        except KeyError:
            raise MalformedForm("Form does not contain questions")

        if not isinstance(questions, list):
            raise MalformedForm("Form questions must be a list")

        self.questions = tuple(QuestionFieldBuilder(q).build() for q in questions)
        self.form = DynamicForm(extracted_fields=self.questions)

        # for cascade queryset-ish / django-ish calls
        return self

    @classmethod
    def load_yaml(cls, file_object):
        import yaml

        return cls(yaml.safe_load(file_object.read()))

    @classmethod
    def load_json(cls, file_object):
        import json

        return cls(json.loads(file_object.read()))


"""
Auxiliary functions
"""


def validate_form_path(base_path, path):
    try:
        if path.resolve() < base_path.resolve():
            raise SuspiciousFileOperation(
                "Staff user is attempting forbidden filesystem traversal."
            )
    except RuntimeError:
        raise SuspiciousFileOperation(
            "Staff user tried to trick form path validator in an infinite loop"
        )


def get_full_subject_path(path):
    form_path = settings.PROLOGIN_FORMS_REPOSITORY / path
    validate_form_path(settings.PROLOGIN_FORMS_REPOSITORY, form_path)
    return form_path
