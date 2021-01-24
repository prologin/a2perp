from django import forms
from django.core.exceptions import ValidationError

class SubmissionForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data['file']
        if file and file.content_type != 'application/pdf':
            raise ValidationError('Le fichier envoyé doit être au format PDF.')