from django.conf.urls.defaults import *

def urls_for_partial_date(prefix, view_prefix, name_list, singular=None, general=None):
    """Makes a url pattern for each partial date application.
    
    For example, ufpd(r'^', 'articles.views', 'articles', 'article') returns
       patterns('articles.views',
         (r'^(\d{4})/$',                              'articles_year'),
         (r'^(\d{4})/(\d{1,2})/$',                    'articles_month),
         (r'^(\d{4})/(\d{1,2})/(\d{1,2})/$',          'articles_day'),
         (r'^(\d{4})/(\d{1,2})/(\d{1,2})/([\w-]+)/$', 'article')
       )
    (except that the arguments are named 'year', 'month', 'day', and 'slug')."""
    
    a = []
    
    if general:
        a.append( (prefix + r'/$', name_list) )
    
    regex = prefix
    for time, num_digits in (('year', '4'), ('month', '1,2'), ('day', '1,2')):
        regex += r'(?P<%s>\d{%s})/' % (time, num_digits)
        a += (regex, "%s_%s" % (name_list, num_digits))
    
    if singular:
        a.append( regex + r'(?P<slug>[\w-]+)/$', singular) )
    
    return patterns(view_prefix, *a)

ufpd = urls_for_partial_date


urlpatterns = patterns('',
    (r'^/$', 'articles.views.homepage'),
    
    (r'^issue/$', 'issues.views.today'),
)

urlpatterns += ufpd(r'^', 'articles.views', 'articles', 'article')
urlpatterns += ufpd(r'^announcements/', 'articles.views', 'announcements', 'announcement')
urlpatterns += ufpd(r'^announcements/([\w-]+)/', 'articles.views', 
                      'announcement_kind', general='announcement_kind')
urlpatterns += ufpd(r'^issue/', 'articles.views', 'issues')

urlpatterns += ufpd(r'^polls/', 'polls.views', 'polls', 'poll')
urlpatterns += patterns('polls.views',
    url(r'^polls/(?P<year>\d{4})/(?P<slug>[\w-]+)/$', 'poll', name='poll-details'),
    (r'^polls/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>[\w-]+)/$', 'poll')
)

# category needs to be last, to avoid shadowing others
urlpatterns += ufpd(r'^([\w-]+)/', 'articles.views', 'category', general='category')
