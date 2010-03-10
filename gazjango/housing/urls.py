from django.conf.urls.defaults import *
from gazjango.housing.views      import *
from gazjango.misc.url_helpers import reps

urlpatterns = patterns('',
    (r'^/?$',            list_housing,   {}, 'housing'),
    (r'^new/success/$',  senior_success),
)
