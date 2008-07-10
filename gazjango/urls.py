from django.conf.urls.defaults import *

reps = {
    'year':  r'(?P<year>\d{4})',
    'month': r'(?P<month>\d{1,2})',
    'day':   r'(?P<day>\d{1,2})',
    'slug': r'(?P<slug>[\w-]+)',
    'kind': r'(?P<kind>[\w-]+)',
    'category': r'(?P<category>[\w-]+)',
    'name': r'(?P<name>[\w]+)'
}


urlpatterns = patterns('articles.views',
    (r'^/$', 'homepage'),
    
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/$'       % reps, 'article'),
    (r'^%(year)s/%(month)s/%(day)s/%(slug)s/print/$' % reps, 'print_article'),

    (r'^archives/$', 'archives'),
    (r'^%(year)s/$'                   % reps, 'articles_for_year'),
    (r'^%(year)s/%(month)s/$'         % reps, 'articles_for_month'),
    (r'^%(year)s/%(month)s/%(day)s/$' % reps, 'articles_for_day'),
    
    (r'^announcements/%(year)s/%(month)s/%(slug)s/$'         % reps, 'announcement'),
    (r'^announcements/%(year)s/%(month)s/%(day)s/%(slug)s/$' % reps, 'announcement'),
    
    (r'^announcements/$',                                   'announcements'),
    (r'^announcements/%(year)s/$'                   % reps, 'announcements_for_year'),
    (r'^announcements/%(year)s/%(month)s/$'         % reps, 'announcements_for_month'),
    (r'^announcements/%(year)s/%(month)s/%(day)s/$' % reps, 'announcements_for_day'),
    
    (r'^announcements/%(kind)s/$'                            % reps, 'announcement_kind'),
    (r'^announcements/%(kind)s/%(year)s/$'                   % reps, 'announcement_kind_for_year'),
    (r'^announcements/%(kind)s/%(year)s/%(month)s/$'         % reps, 'announcement_kind_for_month'),
    (r'^announcements/%(kind)s/%(year)s/%(month)s/%(day)s/$' % reps, 'announcement_kind_for_day')
)

urlpatterns += patterns('issues.views',
    (r'^issue/$',                                   'issue_for_today')
    (r'^issue/%(year)s/$'                   % reps, 'issues_for_year'),
    (r'^issue/%(year)s/%(month)s/$'         % reps, 'issues_for_month'),
    (r'^issue/%(year)s/%(month)s/%(day)s/$' % reps, 'issues_for_day'),
)

urlpatterns += patterns('polls.views',
    (r'^polls/%(year)s/%(slug)s/$'                   % reps, 'poll'),
    (r'^polls/%(year)s/%(month)s/%(slug)s/$'         % reps, 'poll'),
    (r'^polls/%(year)s/%(month)s/%(day)s/%(slug)s/$' % reps, 'poll', {}, 'poll-details'),
    
    (r'^polls/%(year)s/$'                   % reps, 'polls_for_year'),
    (r'^polls/%(year)s/%(month)s/$'         % reps, 'polls_for_month'),
    (r'^polls/%(year)s/%(month)s/%(day)s/$' % reps, 'polls_for_day')
)

urlpatterns += patterns('',
    url(r'^accounts/login/$',  'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout'),
    (r'^accounts/manage/$',    'accounts.views.manage'),
    (r'^accounts/register/$',  'accounts.views.register'),
    
    (r'users/%(name)s/$' % reps, 'accounts.views.user_details')
)

# category match needs to be last, to avoid shadowing others
urlpatterns += patterns('articles.views',
    (r'^%(category)s/$'                            % reps, 'category'),
    (r'^%(category)s/%(year)s/$'                   % reps, 'category_for_year'),
    (r'^%(category)s/%(year)s/%(month)s/$'         % reps, 'category_for_month'),
    (r'^%(category)s/%(year)s/%(month)s/%(day)s/$' % reps, 'category_for_day'),
)
