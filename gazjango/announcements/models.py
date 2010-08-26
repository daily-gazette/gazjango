from django.db               import models
from django.utils.safestring import mark_safe
from gazjango.misc.helpers   import set_default_slug

from gazjango.accounts.models import UserProfile
from gazjango.media.models    import MediaFile, ImageFile, MediaBucket

import django.utils.html
import datetime
import random
import re

class PublishedAnnouncementsManager(models.Manager):
    "Deals only with published announcements."
    def get_query_set(self):
        orig = super(PublishedAnnouncementsManager, self).get_query_set()
        return orig.filter(is_published=True)
    
    def now_running(self):
        "Returns published announcements which should now be shown."
        return self.running_on(datetime.date.today())
    
    def running_on(self, date, order=('-date_start', '-date_end')):
        """Returns announcements that should be shown for `date`."""
        return self.filter(date_start__lte=date, date_end__gte=date).order_by(*order)
    
    def get_n(self, n=3):
        "Returns the `n` announcements to be shown."
        running = self.now_running()
        if running.count() >= n:
            return running[:n]
        else:
            new = self.order_by('-date_end', '-date_start').exclude(pk__in=[r.pk for r in running])
            return list(running) + list(new[:n - running.count()])
            
class PublishedPosterManager(models.Manager):
    "Deals only with published posters."
    def get_query_set(self):
        orig = super(PublishedPosterManager, self).get_query_set()
        return orig.filter(is_published=True)

    def now_running(self):
        "Returns published posters which should now be shown."
        return self.running_at(datetime.date.today())
    
    def running_at(self, date):
        return self.filter(date_start__lte=date, date_end__gte=date)
    
    def get_running(self, date=None):
        if not date:
            date = datetime.date.today()
        options = self.running_at(date)
        return random.choice(options) if options else None
    

class StaffAnnouncementsManager(PublishedAnnouncementsManager):
    "A custom manager for dealing only with staff announcements."
    def get_query_set(self):
        orig = super(StaffAnnouncementsManager, self).get_query_set()
        return orig.filter(kind='s')
    

class CommunityAnnouncementsManager(PublishedAnnouncementsManager):
    "A custom manager for dealing only with community announcements."
    def get_query_set(self):
        orig = super(CommunityAnnouncementsManager, self).get_query_set()
        return orig.filter(kind='c')
    

class EventsManager(CommunityAnnouncementsManager):
    "A manager for event announcements."
    def get_query_set(self):
        orig = super(EventsManager, self).get_query_set()
        return orig.exclude(event_date=None)
    

class RegularAnnouncementsManager(CommunityAnnouncementsManager):
    "A manager for standard announcements (not lost-and-found or events)."
    def get_query_set(self):
        orig = super(RegularAnnouncementsManager, self).get_query_set()
        return orig.filter(event_date=None).filter(is_lost_and_found=False)

class LostAndFoundManager(CommunityAnnouncementsManager):
    "A manager that handles lost-and-found announcements."
    def get_query_set(self):
        orig = super(LostAndFoundManager, self).get_query_set()
        return orig.filter(is_lost_and_found=True)

class AdminAnnouncementsManager(PublishedAnnouncementsManager):
    "A custom manager for dealing only with admin announcements."
    def get_query_set(self):
        orig = super(AdminAnnouncementsManager, self).get_query_set()
        return orig.filter(kind='a')
    

class Announcement(models.Model):
    """
    An announcement. The first day it runs is date_start, and the last 
    is date_end. Slugs must be unique per-year.
    
    Slug-uniqueness is technically only enforced on the start-year, but
    as announcements spanning years seem unlikely, this should not be a
    major issue.
    """
    
    ANNOUNCEMENT_KINDS = (
        ('s', 'Gazette Staff'),
        ('c', 'Community'),
        ('a', 'Admin'),
    )
    kind = models.CharField(max_length=1, choices=ANNOUNCEMENT_KINDS, default='c')
    
    title = models.CharField(max_length=100)
    slug  = models.SlugField(unique_for_year="date_start", null=True, max_length=100)
    text  = models.TextField()
    
    sponsor = models.CharField(max_length=50)
    sponsor_url = models.URLField(blank=True, verify_exists=False)
    poster_email = models.EmailField()
    
    date_start = models.DateField(default=datetime.date.today)
    date_end   = models.DateField(default=datetime.date.today)
    
    is_lost_and_found = models.BooleanField(blank=True, default=False)
    
    event_date  = models.DateField(blank=True, null=True)
    event_time  = models.CharField(blank=True, max_length=20)
    event_place = models.CharField(blank=True, max_length=25)
    
    is_published = models.BooleanField(default=False)
    
    objects   = models.Manager()
    published = PublishedAnnouncementsManager()
    staff     = StaffAnnouncementsManager()
    admin     = AdminAnnouncementsManager()
    community = CommunityAnnouncementsManager()
    regular        = RegularAnnouncementsManager()
    events         = EventsManager()
    lost_and_found = LostAndFoundManager()
    
    def is_event(self):
        return bool(self.event_date)
    
    def brief_excerpt(self, num_chars=120, link=True):
        text = django.utils.html.strip_tags(self.text)
        if len(text) <= num_chars:
            return text
        elif link:
            end = '... [<a href="%s">more</a>]' % self.get_absolute_url()
            return text[:(num_chars-7)] + end
        else:
            return text[:(num_chars-4)] + '...'
    
    def long_excerpt(self, num_chars=300, link=True):
        return self.brief_excerpt(num_chars=num_chars, link=link)
    
    def unlinked_excerpt(self, num_chars=120):
        return self.brief_excerpt(num_chars, link=False)
    
    def unlinked_long_excerpt(self, num_chars=300):
        return self.brief_excerpt(num_chars, link=False)
    
    def sponsor_link(self):
        if self.sponsor_url:
            return mark_safe('<a href="%s">%s</a>' % (self.sponsor_url, self.sponsor))
        else:
            return mark_safe(self.sponsor)
    
    def __unicode__(self):
        return self.slug or '<no slug>'
    
    @models.permalink
    def get_absolute_url(self):
        return ('announcement', [str(self.date_start.year), self.slug])
    
    class Meta:
        get_latest_by = 'date_start'
    

_slugger = set_default_slug(lambda x: x.title,
                            lambda x: { 'date_start__year': x.date_start.year })
models.signals.pre_save.connect(_slugger, sender=Announcement)



class Poster(models.Model):
    title        = models.CharField(max_length=90)
    poster       = models.ForeignKey(ImageFile, null=True, blank=True)
    sponsor_name = models.CharField(max_length=100)
    sponsor_url  = models.URLField(blank=True, verify_exists=True)
    sponsor_user = models.ForeignKey(UserProfile)
    
    date_start = models.DateField(default=datetime.date.today)
    date_end   = models.DateField(default=datetime.date.today)
        
    is_published = models.BooleanField(default=False)
    
    related_event = models.ForeignKey(Announcement, null=True, blank=True)
    
    objects = models.Manager()
    published = PublishedPosterManager()
    
    def __unicode__(self):
        return self.title
    
