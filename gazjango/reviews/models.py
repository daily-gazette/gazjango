from django.db                            import models
from django.contrib.contenttypes.models   import ContentType
from django.contrib.sites.models          import Site
from django.contrib.localflavor.us.models import PhoneNumberField
from django.db.models.signals             import pre_save
from gazjango.accounts.models          import UserProfile
from gazjango.articles.models.stories  import Article
from gazjango.misc.helpers             import avg
from gazjango.misc.templatetags.extras import join_authors
from gazjango.tagging.models           import Tag
import datetime
import urllib
import urllib2 # yeah, we need both
import settings

GEOCODE_REQUEST_URL = "http://maps.google.com/maps/geo?q=%(req)s&output=csv&key=%(key)s"

class Establishment(models.Model):
    "Represents a business in the Swarthmore area, or that caters to Swarthmore students."
    slug = models.SlugField()
    
    "Basic Information"
    name = models.CharField(max_length=100)
    TYPE_CHOICES = (
        ('r',"Restaurant"),
        ('t',"Theatre"),
        ('g',"Gift"),
        ('h',"Hotel"),
        ('b',"Big Box"),
        ('h',"Barbers and Salons"),
        ('m',"Mailing")
    )
    establishment_type = models.CharField(max_length=1, choices=TYPE_CHOICES, blank=False)
    
    street_address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=100, blank=True)
    # TODO: make this use localflavor.us.forms.USZipCodeField
    
    ACCESS_CHOICES = (
        ('w', "Walking"),
        ('p', "Public Transportation"),
        ('d', "Driving"),
    )
    access = models.CharField(max_length=1, choices=ACCESS_CHOICES)
    
    phone = PhoneNumberField(blank=True)
    link = models.URLField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    other_info = models.TextField(blank=True)
    
    auto_geocode = models.BooleanField(default=True, blank=True,
        help_text="Automatically derive the latitude/longitude from the address above. "
                  "Note that this overrides any manual setting.")
    latitude = models.CharField(max_length=100, blank=True)
    longitude = models.CharField(max_length=100, blank=True)
    
    def geocode(self):
        if self.street_address:
            loc = (self.street_address, self.zip_code or self.city)
            url = GEOCODE_REQUEST_URL % {
                'req': urllib.quote_plus("%s, %s" % loc),
                'key': settings.GMAPS_API_KEY
            }
            data = urllib2.urlopen(url).read()
            response_code, accuracy, latitude, longitude = data.split(',')
            self.latitude = latitude
            self.longitude = longitude
    
    def avg_cost(self):
        return avg(int(v) for v in self.reviews.values_list('cost', flat=True))
    
    def avg_rating(self):
        return avg(int(v) for v in self.reviews.values_list('rating', flat=True))
    
    def tag_names(self):
        return ', '.join(self.tags.values_list('name', flat=True))
    
    def __unicode__(self):
        return self.name
    

# limit us to tags in valid groups
# we can't do this in the model definition, as Establishment isn't yet defined
# NOTE: this is kind of monkeypatchy and might break in future djangos
Establishment.tags.field.rel.limit_choices_to = { 
    'group__content_type': ContentType.objects.get_for_model(Establishment)
}

def geocode(sender, instance, **kwargs):
    if instance.auto_geocode:
        instance.geocode()
models.signals.pre_save.connect(geocode, sender=Establishment)


class Review(models.Model):
    "Represents the review of an establishment."
    slug = models.SlugField()
    
    establishment = models.ForeignKey(Establishment,related_name="reviews")
    
    COST_CHOICES = (
        ('1',"$"),
        ('2',"$$"),
        ('3',"$$$"),
        ('4',"$$$$")
    )
    cost = models.CharField(max_length=1, choices=COST_CHOICES)
    
    RATING_CHOICES = (
        ('1',"*"),
        ('2',"**"),
        ('3',"***"),
        ('4',"****"),
        ('5',"*****")
    )
    rating = models.CharField(max_length=1, choices=RATING_CHOICES)
    
    reviewer = models.ForeignKey(UserProfile, related_name="reviews")
    
    review_summary = models.TextField(blank=True) 
    review_text = models.TextField(blank=True)   
    
    def __unicode__(self):
        return self.slug
    
