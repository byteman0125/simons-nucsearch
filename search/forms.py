from django import forms

class RegexForm(forms.Form):
    pattern = forms.CharField(
        label='Regex pattern',
        widget=forms.TextInput(attrs={'placeholder': '(AATCGA|GGCAT)', 'size': 50}),
        help_text='Python regex, e.g. (AATCGA|GGCAT)'
    )
