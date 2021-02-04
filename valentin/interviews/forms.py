from django import forms
from . import models

class InterviewerProfile(forms.ModelForm):
    class Meta:
        model = models.Interviewer
        fields = ['meet_link',]

class IntervierwerDispoSelection(forms.Form):

    def __init__(self, *args, **kwargs):
        slot_choices = kwargs.pop('slot_choices')
        super().__init__(*args, **kwargs)
        self.fields['slot_choices'] = forms.MultipleChoiceField(choices=slot_choices, required=False, widget=forms.CheckboxSelectMultiple())

class ContestantSlotSelection(forms.Form):

    def __init__(self, *args, **kwargs):
        slot_choices = kwargs.pop('slot_choices')
        super().__init__(*args, **kwargs)
        self.fields['slot_choice'] = forms.ChoiceField(choices=slot_choices, required=True, widget=forms.RadioSelect())

class GradingForm(forms.ModelForm):
    class Meta:
        model = models.InterviewScore
        fields = ['grade', 'comments']
