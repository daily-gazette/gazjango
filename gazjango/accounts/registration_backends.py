from gazjango.accounts.models import UserProfile, UserKind
from gazjango.options.helpers import new_user_groups
from gazjango.subscriptions.models import Subscriber

from registration.backends.default import DefaultBackend

class RegistrationWithProfileBackend(DefaultBackend):
    def register(self, request, **kwargs):
        """
        Creates a User and UserProfile for a new registration, based on
        `kwargs`.
        
        All of the User logic from the superclass is done; then we set the
        User's `first_name` and `last_name` (based on a single `name`
        argument), and create a UserProfile based on `kind` (one of
        UserKind.KINDS) and, optionally, `year`. We also set the User's groups.
        """
        sup = super(RegistrationWithProfileBackend, self)
        user = sup.register(request, **kwargs)
        
        user.first_name, user.last_name = (kwargs['name'] + ' ').split(' ', 1)
        user.groups = new_user_groups()
        user.save()
        
        kind_args = { 'kind': kwargs['kind'] }
        if kind_args['kind'] in ('s', 'a'):
            kind_args['year'] = kwargs.get('year', None)
        kind = UserKind.objects.get_or_create(**kind_args)[0]
        profile = user.userprofile_set.create(kind=kind)

        if kwargs['subscribe']:
            Subscriber.objects.create(user=profile, receive='i',
                    racy_content = kwargs['kind'] in ('s','k'),
                    is_confirmed=False)
        
        return user
