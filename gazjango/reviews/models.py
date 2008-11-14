from django.db                         import models
from django.contrib.sites.models       import Site
from gazjango.articles.models.stories  import Article
from gazjango.misc.templatetags.extras import join_authors
import datetime

class Establishment(models.Model):
    "Represents a business in the Swarthmore area, or that caters to Swarthmore students."
    slug = models.SlugField()

    "Basic Information"
    name = models.CharField(max_length=100, blank=True)
    TYPE_CHOICES = (
        ('r',"Restaurant")
        ('t',"Theatre")
        ('g',"Gift")
        ('h',"Hotel")
        ('b',"Big Box")
        ('h',"Barbers and Salons")
        ('m',"Mailing")
    )
    establishment_type = models.CharField(max_length=1,choices=TYPE_CHOICES,blank=False)
    
    street_address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=100, blank=True)
    
    ACCESS_CHOICES = (
        ('w',"Walking")
        ('d',"Driving")
        ('p',"Public Transportation")
    )
    access = models.CharField(max_length=1,choices=ACCESS_CHOICES,blank=False)
    
    phone = models.CharField(max_length=100, blank=True)
    link = models.CharField(max_length=100, blank=True)
    
    other_info = models.TextField(blank=True)
        
    def avg_cost(self):
        return sum(self.reviews.filter(cost=str(i)).count() for i in range(1, 6) / self.reviews.count()
        
    def avg_rating(self):
        return sum(self.reviews.filter(rating=str(i)).count() for i in range(1, 6) / self.reviews.count()
    
    def __unicode__(self):
        return self.name()
        
class Review(models.Model):
    "represents the review of an establishment"
    slug = models.SlugField()
    
    establishment = models.ForeignKey(Establishment,related_name="reviews")
    
    COST_CHOICES = (
        ('1',"$"),
        ('2',"$$"),
        ('3',"$$$"),
        ('4',"$$$$")
    )
    cost = models.CharField(max_length=1,choices=COST_CHOICES,blank=False)
    
    RATING_CHOICES = (
        ('1',"*"),
        ('2',"**"),
        ('3',"***"),
        ('4',"****"),
        ('5',"*****")
    )
    rating = models.CharField(max_length=1,choices=RATING_CHOICES,blank=False)
    
    reviewer = models.ManyToManyField(UserProfile, blank=True, related_name="reviews")
    
    review_summary = models.TextField(blank=True) 
    review_text = models.TextField(blank=True)   

    def __unicode__(self):
        return self.slug
