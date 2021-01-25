from django.core.exceptions import ValidationError
from . import file_forms

def validate_form(path):
    try:
        form = None
        with open(file_forms.get_full_subject_path(path)) as f:
            form = file_forms.FormBuilder.load_yaml(f)

            # raises ValidationError children exceptions
            form.build()
    except OSError:
        raise ValidationError('Failed to open file at given path.')
