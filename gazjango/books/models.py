from django.db                      import models
from django.db.models               import signals, Q
from django.template.defaultfilters import slugify

from gazjango.accounts.models import UserProfile
from gazjango.misc.helpers    import set_default_slug
from gazjango.tagging.models  import Tag

import datetime

class PublishedBooksManager(models.Manager):
    "Deals only with published job listings."
    def get_query_set(self):
        orig = super(PublishedBooksManager, self).get_query_set()
        return orig.filter(is_published=True)
    
    def get_for_show(self, num=5, cutoff=None, base_date=None):
        """
        Gets the `num` most recent unsold Books.
        
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
                      .filter(Q(sold_at=None) | Q(sold_at__gte=base_date))
        if cutoff:
            results = results.filter(pub_date__gte=cutoff)
        
        return results[:num] if num else results
    

class UnsoldBooksManager(PublishedBooksManager):
    "Deals only with published, unsold books in the exchange."
    def get_query_set(self):
        orig = super(UnsoldBooksManager, self).get_query_set()
        return orig.filter(sold_at=None)
    

class BookListing(models.Model):
    "A book being advertised."
    
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, max_length=100)
    
    seller = models.ForeignKey(UserProfile, related_name="books")
    
    description = models.TextField(blank=True)
    
    # TODO: limit to tags for departments only
    departments = models.ManyToManyField(Tag, blank=True)
    
    # EVENTUAL: use a smarter way of setting classes for books
    classes = models.CharField(max_length=100, blank=True)
    
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    sold_at = models.DateTimeField(blank=True, null=True, default=None)
    
    cost = models.CharField(max_length=25, blank=True)
    
    CONDITION_CHOICES = (
        ('1', "Poor: Complete but severly damaged"),
        ('2', "Fair: Has all text pages, may be missing cover or end pages"),
        ('3', "Good: Complete but well worn"),
        ('4', "Very Good: Worn but untorn, minimal or no marks"),
        ('5', "As New"),
    )
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES, blank=False)
    
    is_published = models.BooleanField(default=True)
    
    objects = models.Manager()
    published = PublishedBooksManager()
    unsold = UnsoldBooksManager()
    
    def sold(self, date=None):
        sold = self.sold_at
        return sold and sold <= (date or datetime.datetime.now())
    
    @models.permalink
    def get_absolute_url(self):
        return ('books.views.book_details', [self.slug])
    
    def __unicode__(self):
        return self.slug or '<no slug>'
    

_slugger = set_default_slug(lambda x: x.title)
signals.pre_save.connect(_slugger, sender=BookListing)
