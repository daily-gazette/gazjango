from django.db        import models
from django.db.models import permalink
from django.core      import validators
from datetime         import date

class PublishedAnnouncementsManager(models.Manager):
    "Deals only with published announcements."
    def get_query_set(self):
        orig = super(PublishedAnnouncementsManager, self).get_query_set()
        return orig.filter(is_published=True)
    
    def now_running(self):
        "Returns published announcements which should now be shown."
        today = date.today()
        return self.filter(date_start__lte=today, date_end__gte=today)
    

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
    

class Announcement(models.Model):
    """
    An announcement. The first day it runs is date_start, and the last 
    is date_end.
    
    Note that overlapping announcements must have distinct slugs; this is
    enforced at the field level.
    """
    
    ANNOUNCEMENT_KINDS = (
        ('s', 'Staff'),
        ('c', 'Community'),
    )
    kind = models.CharField(max_length=1, choices=ANNOUNCEMENT_KINDS)
    
    title = models.CharField(blank=True, max_length=100)
    slug  = models.SlugField()
    text  = models.TextField()
    
    sponsor = models.CharField(max_length=50)
    sponsor_url = models.URLField(blank=True, verify_exists=True)
    
    date_start = models.DateField(default=date.today)
    date_end   = models.DateField(default=date.today)
    
    event_date  = models.DateField(blank=True, null=True)
    event_time  = models.CharField(blank=True, max_length=20)
    event_place = models.CharField(blank=True, max_length=25)
    
    is_published = models.BooleanField(default=True)
    
    objects = models.Manager()
    published = PublishedAnnouncementsManager()
    staff = StaffAnnouncementsManager()
    community = CommunityAnnouncementsManager()
    
    def is_event(self):
        return (True if self.event_date else False)
    
    def brief_excerpt(self, num_chars=120, link=True):
        if len(self.text) <= num_chars:
            return self.text
        elif link:
            end = '... [<a href="%s">more</a>]' % self.get_absolute_url()
            return self.text[:(num_chars-7)] + end
        else:
            return self.text[:(num_chars-4)] + '...'
    
    def __unicode__(self):
        return self.slug
    
    @permalink
    def get_absolute_url(self):
        d = self.date_start
        a = [str(x) for x in (d.year, d.month)]
        return ('announcement', a + [self.slug])
    
