
from django import forms
from ..models import Choice


class VoteForm(forms.Form):

    choice = forms.ModelChoiceField(
        queryset=Choice.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None,
        label='Izaberi odgovor'
    )

    def __init__(self, *args, poll=None, **kwargs):
        super().__init__(*args, **kwargs)

        if poll:
            self.fields['choice'].queryset = poll.choices.all()
