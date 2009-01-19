from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify
from gazjango.misc.helpers import set_default_slug
from gazjango.tagging.models           import Tag
import datetime

class PublishedBookManager(models.Manager):
    "Deals only with published job listings."
    def get_query_set(self):
        orig = super(PublishedBooksManager, self).get_query_set()
        return orig.filter(is_published=True)
    
    def get_for_show(self, num=5, cutoff=None, base_date=None):
        """
        Gets the `num` most recent unfilled Books, but if there aren't
        that many, gets filled ones. 
        
        If `cutoff` is passed, exclude objects older than that date / 
        more than that timedelta since now; if `num` is None or 0, don't 
        limit the number.
        
        If `base_date` is passed, pretend that today is that date. (This
        messes up the is_filled bit, obviously, at least until we decide
        to transfer to storing when objects are filled...that's a todo.)
        """
        if not base_date:
            base_date = datetime.datetime.now()
        results = self.order_by('is_sold', '-pub_date')
        results = results.filter(pub_date__lte=base_date)
        if cutoff:
            if isinstance(cutoff, datetime.timedelta):
                cutoff = base_date - cutoff
            results = results.filter(pub_date__gte=cutoff)
        return results[:num] if num else results
    

class UnsoldBookManager(PublishedBooksManager):
    "Deals only with published, unsold books in the exchange."
    def get_query_set(self):
        orig = super(UnfilledBooksManager, self).get_query_set()
        return orig.filter(is_filled=False)
    

class BookListing(models.Model):
    "A book being advertised."
    
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, max_length=100)
    
    book_seller = models.ForeignKey(UserProfile, related_name="book-seller")
    
    description = models.TextField()
    department = models.ManyToManyField(Tag, blank=True)
    classes = models.CharField(max_length=50, blank=True) # This seems like a poor way to do it, but I don't want to make it too complicated
    # TODO: Set it so only department tags show up for selecting a department.
    
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    is_sold = models.BooleanField(default=False, blank=True)
    
    cost  = models.CharField(max_length=25, blank=True)
    
    CONDITION_CHOICES = (
        ('1',"Poor: Complete but severly damaged"),
        ('2',"Fair: Has all text pages, may be missing cover or end pages"),
        ('3',"Good: Complete but well worn"),
        ('4',"Very Good: Worn but untorn"),
        ('5',"As New")
    )
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES)
    
    
    is_published = models.BooleanField(default=False)
    
    objects = models.Manager()
    published = PublishedBooksManager()
    unfilled = UnfilledBooksManager()
    
    @models.permalink
    def get_absolute_url(self):
        return ('Books.views.book_details', [self.slug])
    
    def __unicode__(self):
        return self.slug or '<no slug>'

_slugger = set_default_slug(lambda x: x.name)
signals.post_init.connect(_slugger, sender=BookListing)
