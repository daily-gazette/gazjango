from django.conf.urls.defaults import *
from gazjango.seniors.views      import *
from gazjango.misc.url_helpers import reps

urlpatterns = patterns('',
    (r'^/?$',                    list_seniors),
    (r'^new/success/$',          senior_success),
)
