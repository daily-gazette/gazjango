import datetime

from django.db import models
from django.db.models import permalink

from gazjango.community.managers import EntryManager, PublishedEntryManager
from gazjango.community.sources import import_source_modules

class Entry(models.Model):
    STATUS_CHOICES = (
        (1, 'Draft'),
        (2, 'Public'),
    )
    
    # For All
    title = models.CharField(max_length=200, blank=True,
        help_text="Main text, or Title, of your entry.")
    timestamp = models.DateTimeField(blank=True,
        help_text="Timestamp for your entry. This is how we pull items out of the DB.")
    description = models.TextField(blank=True,
        help_text="Description, or subtext, of your entry.")
    status = models.IntegerField('status', choices=STATUS_CHOICES, default=2)
    
    # For Services
    owner_user = models.CharField(max_length=100, blank=True,
        help_text="Here we store the username used for the webservice, for this entry.")
    url = models.URLField(verify_exists=False, blank=True,
        help_text="URL for the original item.")
    source_type = models.CharField(max_length=100, blank=True, default="post",
        help_text="Type of entry.")
    
    objects   = EntryManager()
    published = PublishedEntryManager()
    
    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']
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
