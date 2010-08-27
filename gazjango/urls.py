from django.conf.urls.defaults import *
from django.contrib            import admin
from django.conf import settings

from gazjango.articles.feeds      import MainFeed, LatestStoriesFeed, SectionFeed
from gazjango.articles.feeds      import SectionLatestFeed, TameFeed
from gazjango.announcements.feeds import AnnouncementsFeed, EventsFeed, NeedsApprovalFeed
from gazjango.accounts.forms      import RegistrationFormWithProfile
from gazjango.jobs.feeds          import JobsFeed
from gazjango.misc.url_helpers    import reps

admin.autodiscover()
urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {
        'packages': ('registration',),
    }),
)

feeds = {
    'main': MainFeed,
    'latest': LatestStoriesFeed,
    'section': SectionFeed,
    'section-latest': SectionLatestFeed,
    'jobs': JobsFeed,
    'dashboard': MainFeed,
    'faculty-dashboard': TameFeed,
    'announcements': AnnouncementsFeed,
    'events': EventsFeed,
    'secret-lol_approval': NeedsApprovalFeed,
}
urlpatterns += patterns('',
    (r'^feeds/(?P<url>.*)(?:\.xml|\.rss|/)$', 'django.contrib.syndication.views.feed',
        {'feed_dict': feeds}),
)

urlpatterns += patterns('facebook_connect.views',
    (r'^xd_receiver\.html$', 'xd_receiver'),
)

urlpatterns += patterns('articles.views',
    (r'^$', 'homepage'),
    # (r'^$', 'april_fools'),
    (r'^search/$', 'search', {}, 'search'),
    
    (r'^%(ymds)s/$'          % reps, 'article', {}, 'article'),
    (r'^%(ymds)s/%(num)s/$'  % reps, 'article', {}, 'photospread'),
    (r'^%(ymds)s/print/$'    % reps, 'article', {'print_view': True}, 'print'),
    (r'^%(ymds)s/email/$'    % reps, 'email_article', {}, 'email'),
    
    (r'^staff/new/$', 'concept_save_page'),
    (r'^staff/$', 'staff'),
    (r'^aprilfools/$', 'april_fools'),
    (r'^staff/mail/$', 'staff_mail'),
)

urlpatterns += patterns('comments.views',
    (r'^comments/$',                 'comment_page'),
    (r'^%(ymds)s/comment/$'         % reps, 'post_comment'),
    (r'^%(ymds)s/comment/captcha/$' % reps, 'show_captcha'),
    (r'^%(ymds)s/comments/(%(num)s/)?$'                         % reps, 'comments_for_article'),
    (r'^%(ymds)s/show-comment/%(num)s/$'                        % reps, 'get_comment_text'),
    (r'^%(ymds)s/vote-comment/%(num)s/(?P<val>up|down|clear)/$' % reps, 'vote_on_comment'),
    (r'^%(ymds)s/approve-comment/%(num)s/(?:%(val-b)s/)?$'      % reps, 'approve_comment'),
)

urlpatterns += patterns('announcements.views',
    (r'^around/$', 'around_swarthmore'),
    (r'^announcements/new/$', 'submit_announcement', {}, 'submit-announcement'),
    (r'^announcements/new/success/$', 'announcement_success', {}, 'announcement-success'),

    (r'^posters/new/$',         'submit_poster',  {}, 'submit-poster'),
    (r'^posters/new/success/$', 'poster_success', {}, 'poster-success'),

    (r'^announcements/%(year)s/%(slug)s/$'                   % reps, 'announcement', {}, 'announcement'),
    (r'^announcements/%(year)s/%(month)s/%(slug)s/$'         % reps, 'announcement'),
    (r'^announcements/%(year)s/%(month)s/%(day)s/%(slug)s/$' % reps, 'announcement'),
    
    (r'announcements/$', 'list_announcements', {}, 'announcements')
    
    # (r'^announcements/$', 'list_announcements', {'order': 'descending', 'kind': 'c'}, 'announcements'),
    # 
    # (r'^announcements/%(year)s/$'                   % reps, 'list_announcements', {'kind': 'c'}),
    # (r'^announcements/%(year)s/%(month)s/$'         % reps, 'list_announcements', {'kind': 'c'}),
    # (r'^announcements/%(year)s/%(month)s/%(day)s/$' % reps, 'list_announcements', {'kind': 'c'}),
    # 
    # (r'^announcements/%(kind)s/$'                            % reps, 'list_announcements'),
    # (r'^announcements/%(kind)s/%(year)s/$'                   % reps, 'list_announcements'),
    # (r'^announcements/%(kind)s/%(year)s/%(month)s/$'         % reps, 'list_announcements'),
    # (r'^announcements/%(kind)s/%(year)s/%(month)s/%(day)s/$' % reps, 'list_announcements'),
)

urlpatterns += patterns('issues.views',
    (r'^issue/$',                                         'latest_issue'),
    (r'^issue/plain/$',                                   'latest_issue', {'plain': True}),
    (r'^issue/%(year)s/%(month)s/%(day)s/$'       % reps, 'issue_for_date', {}, 'issue'),
    (r'^issue/%(year)s/%(month)s/%(day)s/plain/$' % reps, 'issue_for_date', {'plain': True}),
    
    (r'^issue/preview/$',       'preview_issue'),
    (r'^issue/preview/plain/$', 'preview_issue', {'plain': True}),
    
    (r'^rsd/$',                                         'show_rsd', {}, 'rsd-today'),
    (r'^rsd/plain/$',                                   'show_rsd', {'plain': True}),
    (r'^rsd/%(year)s/%(month)s/%(day)s/$'       % reps, 'show_rsd', {}, 'rsd'),
    (r'^rsd/%(year)s/%(month)s/%(day)s/plain/$' % reps, 'show_rsd', {'plain': True}),
    
    (r'^rsd-events/$',                                         'show_events', {}, 'rsd-events-today'),
    (r'^rsd-events/plain/$',                                   'show_events', {'plain': True}),
    (r'^rsd-events/%(year)s/%(month)s/%(day)s/$'       % reps, 'show_events', {}, 'rsd-events'),
    (r'^rsd-events/%(year)s/%(month)s/%(day)s/plain/$' % reps, 'show_events', {'plain': True}),
    
    (r'^rsd-full/$',                                         'show_combined', {}, 'rsd-full-today'),
    (r'^rsd-full/plain/$',                                   'show_combined', {'plain': True}),
    (r'^rsd-full/%(year)s/%(month)s/%(day)s/$'       % reps, 'show_combined', {}, 'rsd-full'),
    (r'^rsd-full/%(year)s/%(month)s/%(day)s/plain/$' % reps, 'show_combined', {'plain': True}),
    
    (r'^menu/$', 'menu_partial'),
    (r'^events/$', 'events_partial')
)

urlpatterns += patterns('polls.views',
    (r'^polls/%(year)s/%(slug)s/results/$' % reps, 'poll_results', {}, 'poll-results'),
    (r'^polls/%(year)s/%(slug)s/submit/$'  % reps, 'submit_poll', {}, 'submit-poll'),
)

urlpatterns += patterns('',
    (r'^books/', include('books.urls')),
)

urlpatterns += patterns('reviews.views', 
    (r'^reviews/$',                 'reviews',       {}, 'reviews'), 
    (r'^reviews/new/$',             'submit_review'), 
    (r'^reviews/%(slug)s/$' % reps, 'establishment', {}, 'establishment'),
)

urlpatterns += patterns('',
    (r'^screw/', include('screw.urls')),
    (r'^housing/', include('housing.urls')),
)

urlpatterns += patterns('jobs.views',
    (r'^jobs/$', 'list_jobs', {}, 'job_list'),
    (r'^jobs/new/$', 'submit_job', {}, 'submit-job'),
    (r'^jobs/new/success/$', 'job_success'),
    
    (r'^jobs/%(slug)s/$' % reps, 'job_details')
)

urlpatterns += patterns('media.views',
    (r'^files/%(bucket)s/$'          % reps, 'bucket'),
    (r'^files/%(bucket)s/%(slug)s/$' % reps, 'file')
)

urlpatterns += patterns('django.contrib.auth.views',
    (r'^accounts/login/$',  'login', {}, 'login'),
    
    (r'^accounts/reset-password/$',      'password_reset', {}, 'password-reset'),
    (r'^accounts/reset-password/sent/$', 'password_reset_done'),
    (r'^accounts/reset-password/%(uid)s-%(token)s/$' % reps, 'password_reset_confirm', {}, 'password-reset-confirm'),
    (r'^accounts/reset-password/complete/$',                 'password_reset_complete'),
)
urlpatterns += patterns('',
    (r'^accounts/logout/$', 'accounts.views.logout', {'next_page': '/'}, 'logout'),
    (r'^accounts/manage/$', 'accounts.views.manage', {}, 'manage-user'),
    (r'^accounts/', include('accounts.registration_urls')),
    
    (r'^users/%(name)s/$'  % reps, 'accounts.views.user_details', {}, 'user-details'),
    (r'^author/%(name)s/$' % reps, 'accounts.views.user_details')
)

urlpatterns += patterns('',
    (r'^data/authors/$', 'accounts.views.author_completions', {}, 'author-completions'),
    (r'^data/usernames/$', 'accounts.views.username_for_name', {}, 'get-or-make-username'),
    # (r'^data/subsections/%(section)s/$' % reps, 'articles.views.list_subsections', {}, 'list-subsections')
    (r'^data/train-stations\.json$', 'reviews.views.list_trains'),
)

if settings.DEBUG:
    path = settings.BASE +'/static'
    urlpatterns += patterns('django.views.static',
        (r'^static/v2/(?P<path>.*)$',     'serve', {'document_root': path + '/v2'}), 
        (r'^static/css/(?P<path>.*)$',     'serve', {'document_root': path + '/css'}),
        (r'^static/js/(?P<path>.*)$',      'serve', {'document_root': path + '/js'}),
        (r'^static/images/(?P<path>.*)$',  'serve', {'document_root': path + '/images'}),
        (r'^static/uploads/(?P<path>.*)$', 'serve', {'document_root': path + '/../uploads'}),
        (r'^static/admin/(?P<path>.*)$', 'serve',  {'document_root': settings.ADMIN_MEDIA_PATH})
    )
    
# urlpatterns += patterns('athletics.views',
#     (r'^athletics/$',                   'athletics'),
#     (r'^athletics/%(slug)s/$'   % reps, 'team',{},'athletics_team')
# )

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
