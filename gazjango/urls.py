from django.conf.urls.defaults import *
import articles

urlpatterns = patterns('',
                       (r'^(\d{4})/$', 'articles.views.archive_year'),
                       (r'^(\d{4})/(\d{1,2})/$', 'articles.views.archive_month'),
                       (r'^(\d{4})/(\d{1,2})/(\d{1,2})/([\w-]+)/$'),
                       (r'^(\d{4})/(\d{1,2})/(\d{1,2})/([\w-]+)/$', 'articles.views.article_page')
)
