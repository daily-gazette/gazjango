from django.db import models
from datetime  import datetime

class JobListing(models.Model):
    "A job/internship/etc being advertised."
    
    name = models.CharField(blank=True, max_length=100)
    slug = models.SlugField(unique=True)
    
    description = models.TextField()
    
    pub_date = models.DateTimeField(default=datetime.now)
    is_filled = models.BooleanField(default=False)
    
    pay     = models.CharField(max_length=25)
    is_paid = models.BooleanField(default=True)
    
    hours = models.CharField(max_length=25)
    when  = models.CharField(max_length=25)
    where = models.CharField(max_length=50)
    
    at_swat   = models.BooleanField(default=True)
    needs_car = models.BooleanField(default=False)
    
    @models.permalink
    def get_absolute_url(self):
        return ('jobs.views.job_details', [self.slug])
    
    def __unicode__(self):
        return self.slug
    
