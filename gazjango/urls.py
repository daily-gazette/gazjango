from django.conf.urls.defaults import *
import settings, os

reps = {
    'year':  r'(?P<year>\d{4})',
    'month': r'(?P<month>\d{1,2})',
    'day':   r'(?P<day>\d{1,2})',
    
    'slug': r'(?P<slug>[-\w]+)',
    'name': r'(?P<name>[-\w]+)',
    'kind': r'(?P<kind>[-\w]+)',
    'category': r'(?P<category>[-\w]+)',
    'bucket':   r'(?P<bucket>[-\w]+)',
    
    'num': r'(?P<num>\d+)'
}


urlpatterns = patterns('articles.views',
    (r'^$', 'homepage'),
    (r'^search/$', 'search', {}, 'search'),
    
    (r'^menu', 'menu_partial'),
    
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/$'        % reps, 'article'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/comment$' % reps, 'comment'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/print/$'  % reps, 'print_article', {}, 'print'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/email/$'  % reps, 'email_article', {}, 'email'),
    
    (r'^photos/%(year)s/%(month)s/%(day)s/%(slug)s/(?:%(num)s/)?$' % reps, 'spread'),
    
    (r'^archives/$', 'archives', {}, 'archives'),
    (r'^%(year)s/$'                   % reps, 'articles'),
    (r'^%(year)s/%(month)s/$'         % reps, 'articles'),
    (r'^%(year)s/%(month)s/%(day)s/$' % reps, 'articles'),
)

urlpatterns += patterns('announcements.views',
    (r'^announcements/%(year)s/%(month)s/%(slug)s/$'         % reps, 'announcement', {}, 'announcement'),
    (r'^announcements/%(year)s/%(month)s/%(day)s/%(slug)s/$' % reps, 'announcement'),
    
    (r'^announcements/$',                                   'announcements'),
    
    (r'^announcements/%(year)s/$'                   % reps, 'kind_for_year', {'kind': 'community'}),
    (r'^announcements/%(year)s/%(month)s/$'         % reps, 'kind_for_month', {'kind': 'community'}),
    (r'^announcements/%(year)s/%(month)s/%(day)s/$' % reps, 'kind_for_day', {'kind': 'community'}),
    
    (r'^announcements/%(kind)s/$'                            % reps, 'kind'),
    (r'^announcements/%(kind)s/%(year)s/$'                   % reps, 'kind_for_year'),
    (r'^announcements/%(kind)s/%(year)s/%(month)s/$'         % reps, 'kind_for_month'),
    (r'^announcements/%(kind)s/%(year)s/%(month)s/%(day)s/$' % reps, 'kind_for_day')
)

urlpatterns += patterns('issues.views',
    (r'^issue/$',                                   'issue_for_today'),
    (r'^issue/%(year)s/$'                   % reps, 'issues_for_year'),
    (r'^issue/%(year)s/%(month)s/$'         % reps, 'issues_for_month'),
    (r'^issue/%(year)s/%(month)s/%(day)s/$' % reps, 'issues_for_day', {}, 'issue'),
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
    (r'jobs/$',                               'list_jobs', {}, 'job_list'),
    (r'jobs/list/(?P<options>(?:[\w-]+/)*)$', 'list_jobs'),
    (r'jobs/%(slug)s/$' % reps,               'job_details')
)

urlpatterns += patterns('media.views',
    (r'^files/%(bucket)s/$'          % reps, 'bucket'),
    (r'^files/%(bucket)s/%(slug)s/$' % reps, 'file')
)

urlpatterns += patterns('',
    (r'^accounts/login/$',    'django.contrib.auth.views.login',  {}, 'login'),
    (r'^accounts/logout/$',   'django.contrib.auth.views.logout', {}, 'logout'),
    (r'^accounts/manage/$',   'accounts.views.manage', {}, 'manage'),
    (r'^accounts/register/$', 'accounts.views.register', {}, 'register'),
    
    (r'users/%(name)s/$' % reps, 'accounts.views.user_details', 'user-details')
)

if settings.DEBUG:
    path = settings.BASE + "/" + 'static'
    urlpatterns += patterns('django.views.static', 
        (r'^css/(?P<path>.*)$',    'serve', {'document_root': os.path.join(path, 'css')}),
        (r'^js/(?P<path>.*)$',     'serve', {'document_root': os.path.join(path, 'js')}),
        (r'^images/(?P<path>.*)$', 'serve', {'document_root': os.path.join(path, 'images')}),
    )

# category match needs to be last, to avoid shadowing others
urlpatterns += patterns('articles.views',
    (r'^%(category)s/$'                            % reps, 'category', {}, 'category'),
    (r'^%(category)s/%(year)s/$'                   % reps, 'category_for_year'),
    (r'^%(category)s/%(year)s/%(month)s/$'         % reps, 'category_for_month'),
    (r'^%(category)s/%(year)s/%(month)s/%(day)s/$' % reps, 'category_for_day'),
)
