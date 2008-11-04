from django.db        import models
from django.db.models import permalink, signals
from django.utils.safestring        import mark_safe
from django.template.defaultfilters import slugify
import django.utils.html
import datetime
import re

class PublishedAnnouncementsManager(models.Manager):
    "Deals only with published announcements."
    def get_query_set(self):
        orig = super(PublishedAnnouncementsManager, self).get_query_set()
        return orig.filter(is_published=True)
    
    def now_running(self):
        "Returns published announcements which should now be shown."
        t = datetime.date.today()
        return self.filter(date_start__lte=t, date_end__gte=t).order_by('-date_start', '-date_end')
    
    def get_n(self, n=3):
        "Returns the `n` announcements to be shown."
        running = self.now_running()
        if running.count() >= n:
            return running[:n]
        else:
            new = self.order_by('date_end', 'date_start').exclude(pk__in=[r.pk for r in running])
            return list(running) + list(new[:n - running.count()])
    

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
    sponsor_url = models.URLField(blank=True, verify_exists=True)
    poster_email = models.EmailField()
    
    date_start = models.DateField(default=datetime.date.today)
    date_end   = models.DateField(default=datetime.date.today)
    
    event_date  = models.DateField(blank=True, null=True)
    event_time  = models.CharField(blank=True, max_length=20)
    event_place = models.CharField(blank=True, max_length=25)
    
    is_published = models.BooleanField(default=False)
    
    objects = models.Manager()
    published = PublishedAnnouncementsManager()
    staff = StaffAnnouncementsManager()
    community = CommunityAnnouncementsManager()
    admin = AdminAnnouncementsManager()
    
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
        return self.brief_excerpt(num_chars)
    
    def sponsor_link(self):
        if self.sponsor_url:
            return mark_safe('<a href="%s">%s</a>' % (self.sponsor_url, self.sponsor))
        else:
            return mark_safe(self.sponsor)
    
    def __unicode__(self):
        return self.slug or '<no slug>'
    
    @permalink
    def get_absolute_url(self):
        return ('announcement', [str(self.date_start.year), self.slug])
    


def set_default_slug(sender, instance, **kwords):
    if not instance.slug:
        slug = base_slug = slugify(instance.title)
        num = 0
        year = datetime.date.today().year
        while Announcement.objects.filter(slug=slug, date_start__year=year).count():
            num += 1
            slug = "%s-%s" % (base_slug, num)
        instance.slug = slug
signals.post_init.connect(set_default_slug, sender=Announcement)
