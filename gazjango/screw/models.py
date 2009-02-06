from django.db                      import models
from django.db.models               import signals, Q
from django.template.defaultfilters import slugify

from gazjango.accounts.models import UserProfile
from gazjango.misc.helpers    import set_default_slug

import datetime

class PublishedScrewManager(models.Manager):
    "Deals only with published names in the screw listings."
    def get_query_set(self):
        orig = super(PublishedScrewManager, self).get_query_set()
        return orig.filter(is_published=True)
    
    def get_for_show(self, num=5, cutoff=None, base_date=None):
        """
        Gets the `num` most recent screw names added.
        
        If `cutoff` is passed, exclude objects older than that date / 
        more than that timedelta since now; if `num` is None or 0, don't 
        limit the number.
        
        If `base_date` is passed, pretend that today is that date.
        """
        base_date = base_date or datetime.datetime.now()
        if isinstance(cutoff, datetime.timedelta):
            cutoff = base_date - cutoff
        
        results = self.order_by('-pub_date') \
                      .filter(pub_date__lte=base_date) \
                      .filter(Q(screwed_at=None) | Q(screwed_at__gte=base_date))
        if cutoff:
            results = results.filter(pub_date__gte=cutoff)
        
        return results[:num] if num else results
    

class UnscrewedManager(PublishedScrewManager):
    "Deals only with published, unscrewed names in the database."
    def get_query_set(self):
        orig = super(UnscrewedManager, self).get_query_set()
        return orig.filter(screwed_at=None)
    

class ScrewListing(models.Model):
    "A screwee to be advertised"
    
    screwee = models.ForeignKey(UserProfile, related_name="screwee")
    slug = models.SlugField(unique=True, null=True, max_length=100)
    
    screwer = models.CharField(max_length=100)
                
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    screwed_at = models.DateTimeField(blank=True, null=True, default=None)
        
    CLASS_YEAR = (
        ('1', "2012 - Freshman"),
        ('2', "2011 - Sophomore"),
        ('3', "2010 - Junior"),
        ('4', "2009 - Senior"),
    )
    year = models.CharField(max_length=1, choices=CLASS_YEAR, blank=False)
    
    is_published = models.BooleanField(default=True)
    
    objects = models.Manager()
    published = PublishedScrewManager()
    unscrewed = UnscrewedManager()
    
    def screwed(self, date=None):
        screwed = self.screwed_at
        return screwed and screwed <= (date or datetime.datetime.now())
    
    def __unicode__(self):
        return self.slug or '<no slug>'
    

_slugger = set_default_slug(lambda x: x.screwee)
signals.pre_save.connect(_slugger, sender=ScrewListing)
