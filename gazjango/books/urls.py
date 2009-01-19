from django.conf.urls.defaults import *
from gazjango.books.views      import *
from gazjango.misc.url_helpers import reps

urlpatterns = patterns('',
    (r'^/?$',                list_books),
    (r'^new/$',             submit_book),
    (r'^new/success/$',     book_success),
    (r'^%(slug)s/$' % reps, book_details),
)
