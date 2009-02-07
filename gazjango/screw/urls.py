from django.conf.urls.defaults import *
from gazjango.screw.views      import *
from gazjango.misc.url_helpers import reps

urlpatterns = patterns('',
    (r'^/?$',                    list_screws),
    (r'^new/success/$',          screw_success),
    (r'^%(slug)s/screwed/$' % reps, mark_as_screwed),
)
