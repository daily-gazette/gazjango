from django.conf.urls.defaults import *
from django.contrib import admin
from articles.feeds import MainFeed, LatestStoriesFeed, SectionFeed, SectionLatestFeed
from misc.forms import RegistrationFormWithProfile
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
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/%(num)s/$' % reps, 'show_photospread', {}, 'photospread'),
    
    
    (r'^archives/$', 'articles', {}, 'archives'),
    (r'^(?:archives/)?%(year)s/$'                   % reps, 'articles'),
    (r'^(?:archives/)?%(year)s/%(month)s/$'         % reps, 'articles'),
    (r'^(?:archives/)?%(year)s/%(month)s/%(day)s/$' % reps, 'articles'),
)

urlpatterns += patterns('comments.views',
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/show-comment/%(num)s/$' % reps, 'get_comment_text'),
)

urlpatterns += patterns('announcements.views',
    (r'^announcements/new/$', 'submit_announcement', {}, 'submit-announcement'),
    (r'^announcements/new/success/$', 'announcement_success', {}, 'announcement-success'),

    (r'^announcements/%(year)s/%(slug)s/$'                   % reps, 'announcement', {}, 'announcement'),
    (r'^announcements/%(year)s/%(month)s/%(slug)s/$'         % reps, 'announcement'),
    (r'^announcements/%(year)s/%(month)s/%(day)s/%(slug)s/$' % reps, 'announcement'),
    
    (r'^announcements/$', 'list_announcements', {'order': 'descending', 'kind': 'c'}),
    
    (r'^announcements/%(year)s/$'                   % reps, 'list_announcements', {'kind': 'c'}),
    (r'^announcements/%(year)s/%(month)s/$'         % reps, 'list_announcements', {'kind': 'c'}),
    (r'^announcements/%(year)s/%(month)s/%(day)s/$' % reps, 'list_announcements', {'kind': 'c'}),
    
    (r'^announcements/%(kind)s/$'                            % reps, 'list_announcements'),
    (r'^announcements/%(kind)s/%(year)s/$'                   % reps, 'list_announcements'),
    (r'^announcements/%(kind)s/%(year)s/%(month)s/$'         % reps, 'list_announcements'),
    (r'^announcements/%(kind)s/%(year)s/%(month)s/%(day)s/$' % reps, 'list_announcements'),
)

urlpatterns += patterns('issues.views',
    (r'^issue/$',                                   'issue_for_today'),
    (r'^issue/%(year)s/$'                   % reps, 'issues_list'),
    (r'^issue/%(year)s/%(month)s/$'         % reps, 'issues_list'),
    (r'^issue/%(year)s/%(month)s/%(day)s/$' % reps, 'issue', {}, 'issue'),
    
    (r'^menu/$', 'menu_partial'),
    (r'^events/$', 'events_partial')
)

urlpatterns += patterns('polls.views',
    (r'^polls/%(year)s/%(slug)s/results/$' % reps, 'poll_results', {}, 'poll-results'),
    (r'^polls/%(year)s/%(slug)s/submit/$'  % reps, 'submit_poll', {}, 'submit-poll'),
    
)

urlpatterns += patterns('jobs.views',
    (r'^jobs/$', 'list_jobs', {}, 'job_list'),
    (r'^jobs/new/$', 'submit_job', {}, 'submit-job'),
    (r'^jobs/new/success/$', 'job_success'),
    
    (r'^jobs/list/(?P<options>(?:[\w-]+/)*)$', 'list_jobs'),
    (r'^jobs/%(slug)s/$' % reps, 'job_details')
)

urlpatterns += patterns('media.views',
    (r'^files/%(bucket)s/$'          % reps, 'bucket'),
    (r'^files/%(bucket)s/%(slug)s/$' % reps, 'file')
)

urlpatterns += patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {}, 'login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, 'logout'),
    (r'^accounts/manage/$', 'accounts.views.manage', {}, 'manage-user'),
    (r'^accounts/register/$', 'registration.views.register', { 'form_class': RegistrationFormWithProfile }, 'register'),
    
    (r'^accounts/', include('registration.urls')),
    
    (r'^users/%(name)s/$' % reps, 'accounts.views.user_details', {}, 'user-details'),
)

urlpatterns += patterns('',
    (r'^reporter-admin/$', 'accounts.views.admin_index', {}, 'reporter-admin'),
    
    (r'^reporter-admin/write/$', 'articles.views.admin_write_page1', {}, 'write'),
    (r'^reporter-admin/write/1/$', 'articles.views.admin_write_page1'),
    
    (r'^reporter-admin/comments/$', 'comments.views.manage', {}, 'manage-comments'),
    
    (r'^reporter-admin/upload-media/$', 'media.views.show_form', {}, 'upload-media'),
    (r'^reporter-admin/media-bucket/$', 'media.views.show_form', {'kind': 'bucket'}, 'manage-bucket'),
    (r'^reporter-admin/media-bucket/%(slug)s/$' % reps, 'media.views.show_form', {'kind': 'bucket'}),
)

urlpatterns += patterns('',
    (r'^data/authors/$', 'accounts.views.author_completions', {}, 'author-completions'),
    (r'^data/usernames/$', 'accounts.views.username_for_name', {}, 'get-or-make-username'),
    (r'^data/subsections/%(section)s/$' % reps, 'articles.views.list_subsections', {}, 'list-subsections')
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
