from django import forms
from django.contrib.auth.models import Group
from gazjango.accounts.models    import UserProfile, UserKind
from gazjango.options.helpers    import new_user_groups
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
    
    def save(self):
        """
        Call super's save to make a User and a RegistrationProfile,
        then create a UserProfile.
        """
        user = super(RegistrationFormWithProfile, self).save()
        
        names = (self.cleaned_data['name'] + ' ').split(' ', 1)
        user.first_name, user.last_name = names            
        user.groups = new_user_groups()
        user.save()
        
        kind_args = { 'kind': self.cleaned_data['kind'] }
        if kind_args['kind'] in ('s', 'a'):
            kind_args['year'] = self.cleaned_data['year'] or None
        kind = UserKind.objects.get_or_create(**kind_args)[0]
        
        return user.userprofile_set.create(kind=kind)
    
