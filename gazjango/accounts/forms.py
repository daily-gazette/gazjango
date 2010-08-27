from django import forms
from gazjango.accounts.models    import UserKind
from registration.forms import RegistrationForm
import datetime

class RegistrationFormWithProfile(RegistrationForm):
    name = forms.CharField(max_length=50, label='Name')
    kind = forms.ChoiceField(choices=UserKind.KINDS,
                             initial='o',
                             label='Kind of user')
    year = forms.IntegerField(required=False,
                              min_value=1900,
                              max_value=datetime.date.today().year + 6,
                              label='Swat grad year')
    subscribe = forms.BooleanField(required=False,
                                   label="Subscribe me to daily issues")
