from django.db import models
from datetime  import datetime

class PublishedJobsManager(models.Manager):
    "Deals only with published job listings."
    def get_query_set(self):
        orig = super(PublishedJobsManager, self).get_query_set()
        return orig.filter(is_published=True)
    

class UnfilledJobsManager(PublishedJobsManager):
    "Deals only with published, unfilled job listings."
    def get_query_set(self):
        orig = super(UnfilledJobsManager, self).get_query_set()
        return orig.filter(is_filled=False)
    

class JobListing(models.Model):
    "A job/internship/etc being advertised."
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True)
    
    description = models.TextField()
    
    pub_date = models.DateTimeField(default=datetime.now)
    is_filled = models.BooleanField(default=False)
    
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
    
