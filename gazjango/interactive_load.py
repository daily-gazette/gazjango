# ugly, but it's hard to figure out with __import__

from django import forms
from django.core.mail import *
from django.core.urlresolvers import reverse
from django.http import *

def _try_import(*app):
    try:
        exec('from %s import *' % '.'.join(app))
    except ImportError:
        pass

import settings
for app in settings.INSTALLED_APPS:
    if app.startswith('gazjango.'):
        exec('from gazjango import %s' % app[len('gazjango.'):])
    else:
        exec('import %s' % app)
    _try_import(app, 'models')
    _try_import(app, 'forms')

from gazjango.misc.helpers import *
from gazjango.misc.view_helpers import *
from gazjango.options.helpers import *
