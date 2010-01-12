from django import forms
from gazjango.accounts.models    import UserKind
from gazjango.registration.forms import RegistrationForm
import datetime

class RegistrationFormWithProfile(RegistrationForm):
    name = forms.CharField(max_length=50, label='name')
    kind = forms.ChoiceField(choices=UserKind.KINDS,
                             initial='o',
                             label='kind of user')
    year = forms.IntegerField(required=False,
                              min_value=1900,
                              max_value=datetime.date.today().year + 6,
                              label='Swarthmore grad year, if any')
