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
        ('m',"Mailing")
    )
    establishment_type = models.CharField(max_length=1,choices=TYPE_CHOICES,blank=False)
    
    CATEGORY_CHOICES = (
        ('1',"American")
        ('2',"Asian")
        ('3',"Cajun")
        ('4',"Continental")
        ('5',"Fine Dining")
        ('6',"French")
        ('7',"Fusion")
        ('8',"Greek")
        ('9',"Indian")
        ('10',"International")
        ('11',"Irish")
        ('12',"Italian")
        ('13',"Japanese")
        ('14',"Latin")
    )
    restaurant_type = models.CharField(max_length=2,choices=TYPE_CHOICES,blank=False)

    
    street_address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=100, blank=True)
    
    ACCESS_CHOICES = (
        ('w',"Walking")
        ('d',"Driving")
        ('b',"Bus")
        ('t',"Train")
    )
    access = models.CharField(max_length=1,choices=ACCESS_CHOICES,blank=False)
    
    rating = models.IntegerField(blank=True, null=True)
    cost = models.IntegerField(blank=True, null=True)
    
    phone = models.CharField(max_length=100, blank=True)
    link = models.CharField(max_length=100, blank=True)
    
    other_info = models.TextField(blank=True)
    
    review_link = models.ForeignKey(Article, null=True, blank=True, unique=True,
                                related_name="review_link")
    
    def __unicode__(self):
        return self.name()