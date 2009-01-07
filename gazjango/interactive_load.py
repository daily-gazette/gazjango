# ugly, but it's hard to figure out with __import__

from django import forms
from django.core.mail import *
from django.core.urlresolvers import reverse
from django.http import *

import settings
for app in settings.INSTALLED_APPS:
    if app.startswith('gazjango.'):
        exec('from gazjango import %s' % app[len('gazjango.'):])
    else:
        exec('import %s' % app)
    try:
        exec('from %s.models import *' % app)
    except ImportError:
        pass
from gazjango.misc.helpers import *
from gazjango.misc.view_helpers import *
from gazjango.options.helpers import *
