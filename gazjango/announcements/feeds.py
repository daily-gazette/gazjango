from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers         import reverse

from gazjango.announcements.models import Announcement, Poster
from gazjango.jobs.models          import JobListing
from gazjango.reviews.models       import Establishment

import datetime

class AnnouncementsFeed(Feed):
    title = 'Announcements - The Daily Gazette'
    link = '/announcements/'
    description = "Announcements from the Daily Gazette / RSD."
    
    title_template = 'feeds/announcement_title.html'
    description_template = 'feeds/announcement_description.html'
    
    def items(self):
        return Announcement.nonevents.now_running()
    
    def item_author_name(self, item):
        return item.sponsor
    
    def item_author_link(self, item):
        return item.sponsor_url
    

class EventsFeed(Feed):
    title = 'Events Calendar - The Daily Gazette'
    link = '/announcements/'
    description = 'Events from the Daily Gazette / RSD.'
    
    title_template = 'feeds/event_title.html'
    description_template = 'feeds/event_description.html'
    
    def items(self):
        return Announcement.events.now_running()
    
    def item_author_name(self, item):
        return item.sponsor
    
    def item_author_link(self, item):
        return item.sponsor_url
    


_date_to_datetime = lambda d: datetime.datetime(*d.timetuple()[:3])
class NeedsApprovalFeed(Feed):
    title = 'Items Needing Approval - The Daily Gazette'
    link = '/admin/'
    description = 'Things from the Daily Gazette site that need ' \
                  'moderator approval.'
    
    title_template = 'feeds/approval_title.html'
    description_template = 'feeds/approval_description.html'
    
    def items(self):
        # a list like [('a', <Announcement>), ('p', <Poster>), ...]
        announcements = Announcement.objects.filter(is_published=False)
        posters = Poster.objects.filter(is_published=False)
        jobs = JobListing.objects.filter(is_published=False)
        estabs = Establishment.objects.filter(is_published=False)

        date_props = {
            'a': lambda obj: _date_to_datetime(obj.date_start),
            'p': lambda obj: _date_to_datetime(obj.date_start),
            'j': lambda obj: obj.pub_date,
            'e': lambda obj: datetime.datetime.now()-datetime.timedelta(days=2)
        }

        return sorted([('a', a) for a in announcements] +
                      [('p', p) for p in posters] +
                      [('j', j) for j in jobs] +
                      [('e', e) for e in estabs],
                key=lambda (kind, obj): date_props[kind](obj),
                reverse=True
        )
    
    def item_link(self, item):
        kind, obj = item
        # TODO: admin reversing doesn't seem to work. :(
        # return reverse('admin:%s_change' % {
        #     'a': 'announcements_announcement',
        #     'p': 'announcements_poster',
        #     'j': 'jobs_joblisting',
        #     'e': 'reviews_establishment',
        # }[kind], args=(obj.pk,))
        
        return '/admin/%s/%s/' % ({
            'a': 'announcements/announcement',
            'p': 'announcements/poster',
            'j': 'jobs/joblisting',
            'e': 'reviews/establishment'
        }[kind], obj.pk)
            
    
    def item_author_name(self, item):
        kind, obj = item
        if kind == 'a':
            return obj.sponsor
        elif kind == 'p':
            return obj.sponsor_name
        elif kind == 'j':
            return obj.contact_name
        elif kind == 'e':
            return obj.name
    
    def item_author_email(self, item):
        kind, obj = item
        if kind == 'a':
            return obj.poster_email
        elif kind == 'p':
            return obj.sponsor_user.email
        elif kind == 'j':
            return obj.contact_email
        elif kind == 'e':
            return ''
    
    def item_categories(self, item):
        return (item[1]._default_manager.model.__name__,)
    
