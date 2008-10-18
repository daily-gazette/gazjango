from django.db import models
import datetime

class PublishedJobsManager(models.Manager):
    "Deals only with published job listings."
    def get_query_set(self):
        orig = super(PublishedJobsManager, self).get_query_set()
        return orig.filter(is_published=True)
    
    def get_for_show(self, num=5, cutoff=None, base_date=datetime.datetime.now):
        """
        Gets the `num` most recent unfilled jobs, but if there aren't
        that many, gets filled ones. 
        
        If `cutoff` is passed, exclude objects older than that date / 
        more than that timedelta since now; if `num` is None or 0, don't 
        limit the number.
        
        If `base_date` is passed, pretend that today is that date. (This
        messes up the is_filled bit, obviously, at least until we decide
        to transfer to storing when objects are filled...that's a todo.)
        """
        results = self.order_by('is_filled', '-pub_date')
        results = results.filter(pub_date__lte=base_date)
        if cutoff:
            if isinstance(cutoff, datetime.timedelta):
                cutoff = base_date - cutoff
            results = results.filter(pub_date__gte=cutoff)
        return results[:num] if num else results
    

class UnfilledJobsManager(PublishedJobsManager):
    "Deals only with published, unfilled job listings."
    def get_query_set(self):
        orig = super(UnfilledJobsManager, self).get_query_set()
        return orig.filter(is_filled=False)
    

class JobListing(models.Model):
    "A job/internship/etc being advertised."
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, max_length=100)
    
    description = models.TextField()
    
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    # TODO: switch joblistings to a time-filled instead of boolean
    is_filled = models.BooleanField(default=False, blank=True)
    
    pay     = models.CharField(max_length=25, blank=True)
    is_paid = models.BooleanField(default=True, blank=True)
    
    hours = models.CharField(max_length=25, blank=True)
    when  = models.CharField(max_length=25, blank=True)
    where = models.CharField(max_length=50, blank=True)
    
    at_swat   = models.BooleanField(default=True, blank=True)
    needs_car = models.BooleanField(default=False, blank=True)
    
    is_published = models.BooleanField(default=False)
    
    objects = models.Manager()
    published = PublishedJobsManager()
    unfilled = UnfilledJobsManager()
    
    @models.permalink
    def get_absolute_url(self):
        return ('jobs.views.job_details', [self.slug])
    
    def __unicode__(self):
        return self.slug
    
    def get_pay(self):
        return self.pay if self.is_paid else 'None'
    
