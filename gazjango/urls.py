from django.conf.urls.defaults import *
from django.contrib import admin
from articles.feeds import MainFeed, LatestStoriesFeed, SectionFeed, SectionLatestFeed
import settings

admin.autodiscover()
urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
)

feeds = {
    'main': MainFeed,
    'latest': LatestStoriesFeed,
    'section': SectionFeed,
    'section-latest': SectionLatestFeed
}
urlpatterns += patterns('',
    (r'^feeds/(?P<url>.*)(?:\.xml|/)$', 'django.contrib.syndication.views.feed',
        {'feed_dict': feeds}),
)

reps = {
    'year':  r'(?P<year>\d{4})',
    'month': r'(?P<month>\d{1,2})',
    'day':   r'(?P<day>\d{1,2})',
    
    'slug': r'(?P<slug>[-\w]+)',
    'name': r'(?P<name>[-\w]+)',
    'kind': r'(?P<kind>[-\w]+)',
    'bucket': r'(?P<bucket>[-\w]+)',
    'section': r'(?P<section>[-\w]+)',
    'subsection': r'(?P<subsection>[-\w]+)',
    
    'num': r'(?P<num>\d+)'
}


urlpatterns += patterns('articles.views',
    (r'^$', 'homepage'),
    (r'^search/$', 'search', {}, 'search'),
    
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/$'         % reps, 'article', {}, 'article'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/print/$'   % reps, 'article', {'print_view': True}, 'print'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/email/$'   % reps, 'email_article', {}, 'email'),
    
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/show-comment/%(num)s/$' % reps, 'get_comment_text'),
    
    (r'^photos/%(year)s/%(month)s/%(day)s/%(slug)s/(?:%(num)s/)?$' % reps, 'spread'),
    
    (r'^archives/$', 'articles', {}, 'archives'),
    (r'^(?:archives/)?%(year)s/$'                   % reps, 'articles'),
    (r'^(?:archives/)?%(year)s/%(month)s/$'         % reps, 'articles'),
    (r'^(?:archives/)?%(year)s/%(month)s/%(day)s/$' % reps, 'articles'),
)

urlpatterns += patterns('announcements.views',
    (r'^announcements/%(year)s/%(slug)s/$'                   % reps, 'announcement', {}, 'announcement'),
    (r'^announcements/%(year)s/%(month)s/%(slug)s/$'         % reps, 'announcement'),
    (r'^announcements/%(year)s/%(month)s/%(day)s/%(slug)s/$' % reps, 'announcement'),
    
    (r'^announcements/$', 'list_announcements', {'order': 'descending'}),
    
    (r'^announcements/%(year)s/$'                   % reps, 'list_announcements', {'kind': 'community'}),
    (r'^announcements/%(year)s/%(month)s/$'         % reps, 'list_announcements', {'kind': 'community'}),
    (r'^announcements/%(year)s/%(month)s/%(day)s/$' % reps, 'list_announcements', {'kind': 'community'}),
    
    (r'^announcements/%(kind)s/$'                            % reps, 'list_announcements'),
    (r'^announcements/%(kind)s/%(year)s/$'                   % reps, 'list_announcements'),
    (r'^announcements/%(kind)s/%(year)s/%(month)s/$'         % reps, 'list_announcements'),
    (r'^announcements/%(kind)s/%(year)s/%(month)s/%(day)s/$' % reps, 'list_announcements')
)

urlpatterns += patterns('issues.views',
    (r'^issue/$',                                   'issue_for_today'),
    (r'^issue/%(year)s/$'                   % reps, 'issues_list'),
    (r'^issue/%(year)s/%(month)s/$'         % reps, 'issues_list'),
    (r'^issue/%(year)s/%(month)s/%(day)s/$' % reps, 'issue', {}, 'issue'),
    
    (r'^menu/$', 'menu_partial'),
)

urlpatterns += patterns('polls.views',
    (r'^polls/%(year)s/%(slug)s/$'                   % reps, 'poll'),
    (r'^polls/%(year)s/%(month)s/%(slug)s/$'         % reps, 'poll'),
    (r'^polls/%(year)s/%(month)s/%(day)s/%(slug)s/$' % reps, 'poll', {}, 'poll-details'),
    
    (r'^polls/%(year)s/$'                   % reps, 'polls_for_year'),
    (r'^polls/%(year)s/%(month)s/$'         % reps, 'polls_for_month'),
    (r'^polls/%(year)s/%(month)s/%(day)s/$' % reps, 'polls_for_day')
)

urlpatterns += patterns('jobs.views',
    (r'^jobs/$',                               'list_jobs', {}, 'job_list'),
    (r'^jobs/list/(?P<options>(?:[\w-]+/)*)$', 'list_jobs'),
    (r'^jobs/%(slug)s/$' % reps,               'job_details')
)

urlpatterns += patterns('media.views',
    (r'^files/%(bucket)s/$'          % reps, 'bucket'),
    (r'^files/%(bucket)s/%(slug)s/$' % reps, 'file')
)

urlpatterns += patterns('',
    (r'^accounts/login/$',    'django.contrib.auth.views.login',  {},                 'login'),
    (r'^accounts/logout/$',   'django.contrib.auth.views.logout', {'next_page': '/'}, 'logout'),
    (r'^accounts/manage/$',   'accounts.views.manage',            {},                 'manage'),
    (r'^accounts/register/$', 'accounts.views.register',          {},                 'register'),
    
    (r'^users/%(name)s/$' % reps, 'accounts.views.user_details', {}, 'user-details')
)

if settings.DEBUG:
    path = settings.BASE +'/static'
    urlpatterns += patterns('django.views.static', 
        (r'^static/css/(?P<path>.*)$',     'serve', {'document_root': path + '/css'}),
        (r'^static/js/(?P<path>.*)$',      'serve', {'document_root': path + '/js'}),
        (r'^static/images/(?P<path>.*)$',  'serve', {'document_root': path + '/images'}),
        (r'^static/uploads/(?P<path>.*)$', 'serve', {'document_root': path + '/../uploads'}),
        
        (r'^static/admin/(?P<path>.*)$', 'serve',  {'document_root': settings.ADMIN_MEDIA_PATH})
    )

# section match should be last, to avoid shadowing others
urlpatterns += patterns('articles.views',
    (r'^%(section)s/$'                            % reps, 'section', {}, 'section'),
    (r'^%(section)s/%(year)s/$'                   % reps, 'section'),
    (r'^%(section)s/%(year)s/%(month)s/$'         % reps, 'section'),
    (r'^%(section)s/%(year)s/%(month)s/%(day)s/$' % reps, 'section'),
    
    (r'^%(section)s/%(subsection)s/$'                            % reps, 'subsection', {}, 'subsection'),
    (r'^%(section)s/%(subsection)s/%(year)s/$'                   % reps, 'subsection'),
    (r'^%(section)s/%(subsection)s/%(year)s/%(month)s/$'         % reps, 'subsection'),
    (r'^%(section)s/%(subsection)s/%(year)s/%(month)s/%(day)s/$' % reps, 'subsection'),
)
