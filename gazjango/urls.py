from django.conf.urls.defaults import *
import articles, issues

urlpatterns = patterns('',
    (r'^/$', 'articles.views.index'),
    
    (r'^(\d{4})/$',                              'articles.views.archive_year'),
    (r'^(\d{4})/(\d{1,2})/$',                    'articles.views.archive_month'),
    (r'^(\d{4})/(\d{1,2})/(\d{1,2})/$',          'articles.views.archive_day'),
    (r'^(\d{4})/(\d{1,2})/(\d{1,2})/([\w-]+)/$', 'articles.views.article_page'),
    
    (r'^issue/$', 'issues.views.today'),
    (r'^issue/(\d{4})/(\d{1,2})/(\d{1,2})/', 'issues.views.for_date')
)
