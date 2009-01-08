from django.conf.urls.defaults import *
from django.contrib import admin
from gazjango.articles.feeds import MainFeed, LatestStoriesFeed, SectionFeed, SectionLatestFeed, TameFeed
from gazjango.jobs.feeds     import JobsFeed
from gazjango.misc.forms import RegistrationFormWithProfile
from django.conf import settings

admin.autodiscover()
urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
)

feeds = {
    'main': MainFeed,
    'latest': LatestStoriesFeed,
    'section': SectionFeed,
    'section-latest': SectionLatestFeed,
    'jobs': JobsFeed,
    'dashboard': MainFeed,
    'faculty-dashboard': TameFeed,
}
urlpatterns += patterns('',
    (r'^feeds/(?P<url>.*)(?:\.xml|\.rss|/)$', 'django.contrib.syndication.views.feed',
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
    'section': r'(?P<section>[a-zA-Z][-\w]+)',
    'subsection': r'(?P<subsection>[a-zA-Z][-\w]+)',
    
    'num': r'(?P<num>\d+)',
    'uid': r'(?P<uidb36>[a-z0-9]+)',
    'token': r'(?P<token>\w+-\w+)',
}


urlpatterns += patterns('articles.views',
    (r'^$', 'homepage'),
    (r'^search/$', 'search', {}, 'search'),
    
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/$'          % reps, 'article', {}, 'article'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/%(num)s/$'  % reps, 'article', {}, 'photospread'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/print/$'    % reps, 'article', {'print_view': True}, 'print'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/email/$'    % reps, 'email_article', {}, 'email'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/comment/$'  % reps, 'post_comment'),
    
    (r'^staff/$', 'staff'),
)

urlpatterns += patterns('comments.views',
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/comments/(%(num)s/)?$'                         % reps, 'comments_for_article'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/show-comment/%(num)s/$'                        % reps, 'get_comment_text'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/vote-comment/%(num)s/(?P<val>up|down|clear)/$' % reps, 'vote_on_comment'),
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
    (r'^issue/$',                                         'latest_issue'),
    (r'^issue/plain/$',                                   'latest_issue', {'plain': True}),
    (r'^issue/%(year)s/%(month)s/%(day)s/$'       % reps, 'issue_for_date', {}, 'issue'),
    (r'^issue/%(year)s/%(month)s/%(day)s/plain/$' % reps, 'issue_for_date', {'plain': True}),
    
    (r'^issue/preview/$',       'preview_issue'),
    (r'^issue/preview/plain/$', 'preview_issue', {'plain': True}),
    
    (r'^rsd/$',                                         'rsd_now'),
    (r'^rsd/plain/$',                                   'rsd_now', {'plain': True}),
    (r'^rsd/%(year)s/%(month)s/%(day)s/$'       % reps, 'show_rsd', {}, 'rsd'),
    (r'^rsd/%(year)s/%(month)s/%(day)s/plain/$' % reps, 'show_rsd', {'plain': True}),
    
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

urlpatterns += patterns('django.contrib.auth.views',
    (r'^accounts/login/$',  'login', {}, 'login'),
    (r'^accounts/logout/$', 'logout', {'next_page': '/'}, 'logout'),
    
    (r'^accounts/reset-password/$',      'password_reset', {}, 'password-reset'),
    (r'^accounts/reset-password/sent/$', 'password_reset_done'),
    (r'^accounts/reset-password/%(uid)s-%(token)s/$' % reps, 'password_reset_confirm', {}, 'password-reset-confirm'),
    (r'^accounts/reset-password/complete/$',                 'password_reset_complete'),
)
urlpatterns += patterns('',
    (r'^accounts/manage/$', 'accounts.views.manage', {}, 'manage-user'),
    (r'^accounts/register/$', 'registration.views.register', { 'form_class': RegistrationFormWithProfile }, 'register'),
    
    (r'^accounts/', include('registration.urls')),
    
    (r'^users/%(name)s/$'  % reps, 'accounts.views.user_details', {}, 'user-details'),
    (r'^author/%(name)s/$' % reps, 'accounts.views.user_details')
)

urlpatterns += patterns('',
    (r'^data/authors/$', 'accounts.views.author_completions', {}, 'author-completions'),
    (r'^data/usernames/$', 'accounts.views.username_for_name', {}, 'get-or-make-username'),
    # (r'^data/subsections/%(section)s/$' % reps, 'articles.views.list_subsections', {}, 'list-subsections')
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
    
urlpatterns += patterns('athletics.views',
    (r'^athletics/$',                   'athletics'),
    (r'^athletics/%(slug)s/$'   % reps, 'team',{},'athletics_team')
)

urlpatterns += patterns('reviews.views',
    (r'^reviews/$',                   'reviews')
)

# section match should be last, to avoid shadowing others
urlpatterns += patterns('articles.views',
    (r'^archives/$', 'archives', {}, 'archives'),
    (r'^(?:archives/)?%(year)s/$'                   % reps, 'archives'),
    (r'^(?:archives/)?%(year)s/%(month)s/$'         % reps, 'archives'),
    (r'^(?:archives/)?%(year)s/%(month)s/%(day)s/$' % reps, 'archives'),
    (r'^archives/%(section)s/$'                % reps, 'archives'),
    (r'^archives/%(section)s/%(subsection)s/$' % reps, 'archives'),
    (r'^(?:archives/)?%(section)s/(?:%(subsection)s/)?%(year)s/$'                   % reps, 'archives'),
    (r'^(?:archives/)?%(section)s/(?:%(subsection)s/)?%(year)s/%(month)s/$'         % reps, 'archives'),
    (r'^(?:archives/)?%(section)s/(?:%(subsection)s/)?%(year)s/%(month)s/%(day)s/$' % reps, 'archives'),

    (r'^%(section)s/$'                % reps, 'section',    {}, 'section'),
    (r'^%(section)s/%(subsection)s/$' % reps, 'subsection', {}, 'subsection'),
)
