
from django import forms
from django.utils import timezone


class PollForm(forms.Form):

    question = forms.CharField(
        label='Pitanje',
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Unesi pitanje ankete'
        })
    )

    closes_at = forms.DateTimeField(
        label='Anketa se zatvara',
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local'
        })
    )

    choice_1 = forms.CharField(
        label='Odgovor 1',
        max_length=255
    )

    choice_2 = forms.CharField(
        label='Odgovor 2',
        max_length=255
    )

    choice_3 = forms.CharField(
        label='Odgovor 3',
        max_length=255,
        required=False
    )

    choice_4 = forms.CharField(
        label='Odgovor 4',
        max_length=255,
        required=False
    )

    choice_5 = forms.CharField(
        label='Odgovor 5',
        max_length=255,
        required=False
    )

    choice_6 = forms.CharField(
        label='Odgovor 6',
        max_length=255,
        required=False
    )

    def clean_closes_at(self):
        closes_at = self.cleaned_data['closes_at']

        if closes_at <= timezone.now():
            raise forms.ValidationError(
                'Vreme zatvaranja mora biti u budućnosti.'
            )

        return closes_at

    def clean(self):
        cleaned_data = super().clean()

        choices = [
            cleaned_data.get(f'choice_{i}', '').strip()
            for i in range(1, 7)
        ]

        choices = [choice for choice in choices if choice]

        if len(choices) < 2:
            raise forms.ValidationError(
                'Anketa mora imati najmanje 2 odgovora.'
            )

        if len(choices) != len(set(choice.lower() for choice in choices)):
            raise forms.ValidationError(
                'Odgovori ne smeju biti duplirani.'
            )

        cleaned_data['choices'] = choices

        return cleaned_data
