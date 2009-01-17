from django.db                            import models
from django.contrib.contenttypes.models   import ContentType
from django.contrib.sites.models          import Site
from django.contrib.localflavor.us.models import PhoneNumberField
from django.db.models.signals             import pre_save
from django.template.defaultfilters       import slugify
from gazjango.accounts.models          import UserProfile
from gazjango.articles.models.stories  import Article
from gazjango.misc.helpers             import avg, set_default_slug
from gazjango.misc.templatetags.extras import join_authors
from gazjango.reviews.directions       import TRAIN_STATIONS, TRAIN_CHOICES, nearest_station
from gazjango.tagging.models           import Tag
import datetime
import urllib
import urllib2 # yeah, we need both
import settings

GEOCODE_REQUEST_URL = "http://maps.google.com/maps/geo?q=%(req)s&output=csv&key=%(key)s"

class PublishedEstablishmentManager(models.Manager):
    def get_query_set(self):
        reg = super(PublishedEstablishmentManager, self).get_query_set()
        return reg.filter(is_published=True)
    

class Establishment(models.Model):
    "Represents a business in the Swarthmore area, or that caters to Swarthmore students."
    slug = models.SlugField()
    is_published = models.BooleanField(blank=True, default=False,
        help_text="Whether this establishment has been approved to show up on the site.")
    
    name = models.CharField(max_length=100)
    TYPE_CHOICES = (
        ('r',"Restaurant"),
        ('a',"Attractions"),
        ('g',"Grocery"),
        ('h',"Hotel"), 
        ('s',"Hair Care"),
        ('m',"Mailing"),
        ('b',"Bars") 
    )
    establishment_type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
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
    
    def _get_nearest_station(self):
        if not self._nearest_station and self.auto_nearest_station:
            self.find_nearest_station()
        try:
            return TRAIN_STATIONS[self._nearest_station]
        except KeyError:
            return None
    
    def _set_nearest_station(self, val):
        self._nearest_station = val['id']
    
    _nearest_station = models.IntegerField('nearest train station', blank=True,
        choices=TRAIN_CHOICES, help_text="Where to show directions from; only relevant "
                                         "if access is set to public transit.")
    nearest_station = property(_get_nearest_station, _set_nearest_station)
    auto_nearest_station = models.BooleanField(default=True, blank=True,
        help_text="Whether to override the nearest_station choice above with the "
                  "one closest to it (straight-line distance).")
    
    objects = models.Manager()
    published = PublishedEstablishmentManager()
    
    def geocode(self):
        if self.street_address:
            if self.city:
                loc = [self.street_address, self.city, self.zip_code]
            else:
                loc = [self.street_address, self.zip_code]
            url = GEOCODE_REQUEST_URL % {
                'req': urllib.quote_plus(', '.join(loc)),
                'key': settings.GMAPS_API_KEY
            }
            data = urllib2.urlopen(url).read()
            response_code, accuracy, latitude, longitude = data.split(',')
            self.latitude = latitude
            self.longitude = longitude
    
    def find_nearest_station(self):
        if self.latitude and self.longitude:
            self.nearest_station = nearest_station(self.latitude, self.longitude)
    
    def avg_cost(self):
        return avg(int(v) for v in self.reviews.values_list('cost', flat=True))
    
    def avg_rating(self):
        return avg(int(v) for v in self.reviews.values_list('rating', flat=True))
    
    def tag_names(self):
        return ', '.join(self.tags.values_list('name', flat=True))
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('establishment', None, {'slug': self.slug})
    

_slugger = set_default_slug(lambda x: x.name)
models.signals.pre_save.connect(_slugger, sender=Establishment)

# limit us to tags in valid groups
# we can't do this in the model definition, as Establishment isn't yet defined
# NOTE: this is kind of monkeypatchy and might break in future djangos

# FIXME: this breaks syncdb from a blank database, since ContentType doesn't have
#        a table yet
# Establishment.tags.field.rel.limit_choices_to = { 
#     'group__content_type': ContentType.objects.get_for_model(Establishment)
# }

def set_geographical_vars(sender, instance, **kwargs):
    try:
        if instance.auto_geocode:
            instance.geocode()
        if instance.auto_nearest_station:
            instance.find_nearest_station()
    except urllib2.URLError:
        pass
models.signals.pre_save.connect(set_geographical_vars, sender=Establishment)


class Review(models.Model):
    "Represents the review of an establishment."
    establishment = models.ForeignKey(Establishment, related_name="reviews")
    
    COST_CHOICES = (
        ('1',"$"),
        ('2',"$$"),
        ('3',"$$$"),
        ('4',"$$$$"),
        ('5',"$$$$$")
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
    text = models.TextField(blank=True)   
    
    def __unicode__(self):
        return self.reviewer
    
    def get_absolute_url(self):
        return "%s#review-%s" % (self.establishment.get_absolute_url(), self.pk)
    
