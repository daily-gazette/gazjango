from django import forms
from gazjango.registration.forms import RegistrationForm
from gazjango.accounts.models import UserProfile, UserKind
import datetime

class RegistrationFormWithProfile(RegistrationForm):
    name = forms.CharField(max_length=50, label='name')
    kind = forms.ChoiceField(choices=UserKind.KINDS,
                             initial='o',
                             label='kind of user')
    year = forms.IntegerField(required=False,
                              min_value=1900,
                              max_value=datetime.date.today().year + 6,
                              label='Swarthmore grad year (if any)')
    
    def save(self, profile_callback=None):
        """
        Call super's save to make a User and a RegistrationProfile,
        then create a UserProfile.
        
        Ignore the profile_callback, but accept it just in case
        somebody passes it to us.
        """
        def callback(user):
            names = (self.cleaned_data['name'] + ' ').split(' ', 1)
            user.first_name, user.last_name = names
            user.save()
            
            kind_args = { 'kind': self.cleaned_data['kind'] }
            if kind_args['kind'] in ('s', 'a') and self.cleaned_data['year']:
                kind_args['year'] = self.cleaned_data['year']
            kind = UserKind.objects.get_or_create(**kind_args)[0]
            
            profile = user.userprofile_set.create(kind=kind)
        
        user = super(RegistrationFormWithProfile, self) \
                    .save(profile_callback=callback)
    
