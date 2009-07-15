import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import permalink
from django.contrib.auth.models import User

from gazjango.community.managers import EntryManager
from gazjango.community.sources import import_source_modules

class PublishedEntryManager(models.Manager):
    "A custom manager for entries, returning only published articles."
    
    def get_query_set(self):
        orig = super(PublishedEntryManager, self).get_query_set()
        return orig.filter(status__gte=2, timestamp__lte=datetime.datetime.now())
    
    def get_entries(self, base=None, num=10):
        base = base or self
        entries = list(base.order_by('-timestamp')[:num])
        return entries    
    
    def get_photos(self,base=None,num=3):
        base = base or self
        entries = list(base.order_by('-timestamp').filter(source_type="flickrphoto")[:num])
        return entries
        
    def get_tweets(self,base=None,num=3):
        base = base or self
        entries = list(base.order_by('-timestamp').filter(source_type="tweet")[:num])
        return entries

class Entry(models.Model):
    STATUS_CHOICES = (
      (1, 'Draft'),
      (2, 'Public'),
    )
    
    # For All
    title           = models.CharField(max_length=200, help_text="Main text, or Title, of your entry.", blank=True)
    timestamp       = models.DateTimeField(help_text="Timestamp for your entry. This is how we pull items out of the DB.", blank=True)
    description     = models.TextField(help_text="Description, or subtext, of your entry.", blank=True)
    status          = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=2)
    
    # For Services
    owner_user      = models.CharField(max_length=100, help_text="Here we store the username used for the webservice, for this entry.", blank=True)
    url             = models.URLField(verify_exists=False, help_text="URL back to the original item.", blank=True)
    source_type     = models.CharField(max_length=100, help_text="Type of entry.", blank=True, default="post")

    objects         = EntryManager()
    published       = PublishedEntryManager()
    
    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']
        app_label = "community"
        verbose_name_plural = "entries"
        unique_together = [('title', 'timestamp', 'source_type'),]

    def __unicode__(self):
        return u"%s" % self.title

    def __cmp__(self, other_entry):
        return cmp(self.timestamp, other_entry.timestamp)

    @property
    def object(self):
        return getattr(self, self.source_type)

import_source_modules()
