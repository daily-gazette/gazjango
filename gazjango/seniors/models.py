from django.db                      import models
from django.db.models               import signals, Q
from django.template.defaultfilters import slugify
from django.db.models.signals       import pre_save


from gazjango.accounts.models import UserProfile
from gazjango.misc.helpers    import set_default_slug

import datetime
import urllib
import urllib2 # yeah, we need both
import settings


class PublishedSeniorManager(models.Manager):
    "Deals only with published names in the  listings."
    def get_query_set(self):
        orig = super(PublishedSeniorManager, self).get_query_set()
        return orig.filter(is_published=True)
    
class SeniorListing(models.Model):
        
    "A Swarthmore senior."
    
    STATE = (
    ('AL',"ALABAMA"),
    ('AK',"ALASKA"),
    ('AZ',"ARIZONA"),
    ('AR',"ARKANSAS"),
    ('CA',"CALIFORNIA"),
    ('CO',"COLORADO"),
    ('CT',"CONNECTICUT"),
    ('DE',"DELAWARE"),
    ('DC',"DISTRICT OF COLUMBIA"),
    ('FL',"FLORIDA"),
    ('GA',"GEORGIA"),
    ('HI',"HAWAII"),
    ('ID',"IDAHO"),
    ('IL',"ILLINOIS"),
    ('IN',"INDIANA"),
    ('IA',"IOWA"),
    ('KS',"KANSAS"),
    ('KY',"KENTUCKY"),
    ('LA',"LOUISIANA"),
    ('ME',"MAINE"),
    ('MD',"MARYLAND"),
    ('MA',"MASSACHUSETTS"),
    ('MI',"MICHIGAN"),
    ('MN',"MINNESOTA"),
    ('MS',"MISSISSIPPI"),
    ('MO',"MISSOURI"),
    ('MT',"MONTANA"),
    ('NE',"NEBRASKA"),
    ('NV',"NEVADA"),
    ('NH',"NEW HAMPSHIRE"),
    ('NJ',"NEW JERSEY"),
    ('NM',"NEW MEXICO"),
    ('NY',"NEW YORK"),
    ('NC',"NORTH CAROLINA"),
    ('ND',"NORTH DAKOTA"),
    ('OH',"OHIO"),
    ('OK',"OKLAHOMA"),
    ('OR',"OREGON"),
    ('PA',"PENNSYLVANIA"),
    ('PR',"PUERTO RICO"),
    ('RI',"RHODE ISLAND"),
    ('SC',"SOUTH CAROLINA"),
    ('SD',"SOUTH DAKOTA"),
    ('TN',"TENNESSEE"),
    ('TX',"TEXAS"),
    ('UT',"UTAH"),
    ('VT',"VERMONT"),
    ('VA',"VIRGINIA"),
    ('WA',"WASHINGTON"),
    ('DC',"WASHINGTON, DC"),
    ('WV',"WEST VIRGINIA"),
    ('WI',"WISCONSIN"),
    ('WY',"WYOMING"),
    ('NU',"NON-USA"),
    )

    POSITION_TYPE = (
        ('j',"Job"),
        ('i',"Internship"),
        ('g',"Gradiate School"),
        ('o',"Other"),
    )
        
    DATE = (
        ('01',"January"),
        ('02',"February"),
        ('03',"March"),
        ('04',"April"),
        ('05',"May"),
        ('06',"June"),
        ('07',"July"),
        ('08',"August"),
        ('09',"September"),
        ('10',"October"),
        ('11',"November"),
        ('12',"December"),
        ('13',"N/A"),
    )
    
    YEAR = (
        ('1',"2009"),
        ('2',"2010"),
        ('3',"Later"),
    )
    
    senior = models.ForeignKey(UserProfile, related_name="senior")
    
    slug = models.SlugField(unique=True, null=True, max_length=100)
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, choices=STATE, blank=False)
    
    position = models.CharField(max_length=1, choices=POSITION_TYPE, blank=False)
    
    movein-month = models.CharField(max_length=2, choices=DATE, blank=False)
    movein-year  = models.CharField(max_length=2, choices=YEAR, blank=False)
    
    moveout-month = models.CharField(max_length=2, choices=DATE, blank=True)
    moveout-year  = models.CharField(max_length=2, choices=YEAR, blank=True)
    
    is_published = models.BooleanField(default=True)
    
    auto_geocode = models.BooleanField(default=True, blank=True,
        help_text="Automatically derive the latitude/longitude from the address above. "
                  "Note that this overrides any manual setting.")
                  
    latitude = models.CharField(max_length=100, blank=True)
    longitude = models.CharField(max_length=100, blank=True)
    
    objects = models.Manager()
    published = PublishedSeniorManager()
    
    def __unicode__(self):
        return self.slug or '<no slug>'
        
    def geocode(self):
        if self.state is not "NU":
            loc = [self.city, self.state]
            url = GEOCODE_REQUEST_URL % {
                'req': urllib.quote_plus(', '.join(loc)),
                'key': settings.GMAPS_API_KEY
            }
            data = urllib2.urlopen(url).read()
            response_code, accuracy, latitude, longitude = data.split(',')
            self.latitude = latitude
            self.longitude = longitude
    

_slugger = set_default_slug(lambda x: x.senior)
signals.pre_save.connect(_slugger, sender=SeniorListing)

def set_geographical_vars(sender, instance, **kwargs):
    try:
        if instance.auto_geocode:
            instance.geocode()
    except urllib2.URLError:
        pass
models.signals.pre_save.connect(set_geographical_vars, sender=SeniorListing)
