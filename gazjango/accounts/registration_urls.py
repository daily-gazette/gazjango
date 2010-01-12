from gazjango.accounts.forms import RegistrationFormWithProfile
from registration.backends.default.urls import urlpatterns as default_patterns
import copy

# Take registration's default urlpatterns, but change them to what we want, ie
# swap the backend and add a form_class for the registration.
# Nice and hacky.

BACKEND = 'gazjango.accounts.registration_backends.RegistrationWithProfileBackend'

def fix_pattern(pattern):
    # we can't deep-copy these objects, so be careful!
    # not that it really matters that much if we change the original...
    new = copy.copy(pattern)
    new.default_args = copy.deepcopy(pattern.default_args)
    if 'backend' in new.default_args:
        new.default_args['backend'] = BACKEND
    if new.name == 'registration_register':
        new.default_args['form_class'] = RegistrationFormWithProfile
    return new

urlpatterns = [fix_pattern(p) if not hasattr(p, 'urlconf_name') else p for p in default_patterns]
